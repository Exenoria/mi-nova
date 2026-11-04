"""
oido.py - el micrófono de Mika, adaptado para Nova.

Cómo funciona (igual que en Mika 1.5):
  1. Abre el micrófono con sounddevice: 16 kHz, mono, float32.
  2. Lee bloques de 0.1 s y mide el volumen (RMS).
  3. Cuando el volumen pasa del UMBRAL cuenta que hablaste; con ~1 s de
     silencio después de hablar, termina solo (no hace falta soltar nada).
  4. Si nadie habla en ESPERA_VOZ_S segundos, se rinde y devuelve "".
  5. El audio va directo en memoria (array de numpy) al reconocedor:
     no se crea ningún .wav y NO hace falta ffmpeg.

Prueba suelta, sin Nova:   python oido.py
"""
import time

import numpy as np

# ───────────────────────────── Configuración ─────────────────────────────
STT = "whisper"           # "whisper" (faster-whisper, como Mika) o "moonshine" (solo inglés)
IDIOMA = "es"             # idioma de whisper: "es", "en" o None para autodetectar
WHISPER_MODELO = "small"  # "base" si tu PC es lenta
WHISPER_DEVICE = "cpu"    # cpu evita depender de CUDA/cuBLAS y deja la VRAM libre para Nova
MIC_DEVICE = None         # None = micrófono predeterminado de Windows; o un índice/nombre
UMBRAL = 0.015            # volumen (RMS) mínimo para considerar que hablas
SILENCIO_FIN_S = 1.0      # silencio que significa "ya terminé"
ESPERA_VOZ_S = 6.0        # si nadie habla en este tiempo, se rinde
MAX_SEG = 12              # máximo de grabación
SR = 16000
BLOQUE_S = 0.1


class Oido:
    def __init__(self):
        self.modelo = None

    def cargar(self):
        """Carga el reconocedor (la primera vez de whisper descarga el modelo)."""
        if self.modelo is not None:
            return
        if STT == "moonshine":
            import torch
            from transformers import pipeline
            self.modelo = pipeline(
                "automatic-speech-recognition",
                model="UsefulSensors/moonshine-base",
                device=0 if torch.cuda.is_available() else -1,
            )
        else:
            from faster_whisper import WhisperModel
            self.modelo = WhisperModel(WHISPER_MODELO, device=WHISPER_DEVICE, compute_type="int8")

    def grabar(self):
        """Graba hasta que haces silencio. Devuelve un array float32 o None si nadie habló."""
        import sounddevice as sd
        bloque = int(SR * BLOQUE_S)
        bloques_fin = max(1, round(SILENCIO_FIN_S / BLOQUE_S))
        frames, silencio, hablo, pico = [], 0, False, 0.0
        t0 = time.time()
        with sd.InputStream(samplerate=SR, channels=1, dtype="float32", device=MIC_DEVICE) as st:
            while time.time() - t0 < MAX_SEG:
                data, _ = st.read(bloque)
                frames.append(data.copy())
                rms = float(np.sqrt(np.mean(data ** 2)))
                pico = max(pico, rms)
                if rms > UMBRAL:
                    hablo, silencio = True, 0
                elif hablo:
                    silencio += 1
                if hablo and silencio >= bloques_fin:
                    break
                if not hablo and time.time() - t0 > ESPERA_VOZ_S:
                    print(f"[Oido] No detecté voz (volumen máximo {pico:.4f}, umbral {UMBRAL}). "
                          "Si tu voz sí se oye, baja UMBRAL o revisa MIC_DEVICE.")
                    return None
        return np.concatenate(frames)[:, 0]

    def transcribir(self, audio):
        self.cargar()
        if STT == "moonshine":
            return self.modelo({"raw": audio, "sampling_rate": SR})["text"].strip()
        segs, _ = self.modelo.transcribe(audio, language=IDIOMA, vad_filter=True)
        return " ".join(s.text.strip() for s in segs).strip()

    def escuchar(self):
        audio = self.grabar()
        if audio is None:
            return ""
        return self.transcribir(audio)


def describir_error(e):
    detalle = " ".join(str(e).split()) or "sin detalle adicional"
    if isinstance(e, ModuleNotFoundError):
        return (f"Falta {e.name}. Instálalo con: python -m pip install sounddevice faster-whisper")
    return (f"Error de voz ({type(e).__name__}): {detalle[:220]}. "
            "Revisa el dispositivo de entrada y los permisos de micrófono de Windows.")


def bucle_de_voz(oido, responder, tecla="shift"):
    """Tecla -> escuchar -> responder(texto), en bucle (sin recursión)."""
    import traceback
    import keyboard
    while True:
        print(f"Presiona {tecla.capitalize()} y habla (paro solo cuando haces silencio)...")
        keyboard.wait(tecla)
        print("Listening...")
        try:
            texto = oido.escuchar()
        except Exception as e:
            print("[Oido]", describir_error(e))
            traceback.print_exc()
            continue
        if not texto:
            print("No te escuché bien…")
            continue
        print(f"You : {texto}")
        try:
            responder(texto)
        except Exception:
            print("ERROR EN get_response:")
            traceback.print_exc()


if __name__ == "__main__":
    import sounddevice as sd
    print("Micrófonos disponibles:")
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            print(f"  [{i}] {d['name']}")
    o = Oido()
    try:
        print("\nCargando reconocedor (la primera vez descarga el modelo)...")
        o.cargar()
        print("Escuchando... habla ahora.")
        print("Entendí:", repr(o.escuchar()))
    except Exception as e:
        print(describir_error(e))
        raise
