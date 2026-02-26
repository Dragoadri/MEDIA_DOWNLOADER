#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de transcripción de audio usando Whisper
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """Clase para transcribir audio a texto"""

    @staticmethod
    def is_whisper_available():
        """
        Verifica si whisper está disponible en el sistema

        Returns:
            tuple: (disponible: bool, mensaje: str)
        """
        try:
            import whisper
            return True, "Whisper está disponible"
        except ImportError:
            return False, "Whisper no está instalado. Ejecuta: pip install openai-whisper"

    @staticmethod
    def transcribe(audio_path, output_path=None, model_name="base", language="es"):
        """
        Transcribe un archivo de audio a texto

        Args:
            audio_path: Ruta al archivo de audio
            output_path: Ruta donde guardar el archivo de texto (opcional)
            model_name: Modelo de Whisper a usar (tiny, base, small, medium, large)
            language: Idioma del audio (es, en, etc.)

        Returns:
            tuple: (éxito: bool, mensaje: str, texto: str)
        """
        try:
            import whisper

            if not os.path.exists(audio_path):
                return False, f"El archivo de audio no existe: {audio_path}", None

            # Cargar modelo
            model = whisper.load_model(model_name)

            # Transcribir
            result = model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )

            transcription_text = result["text"].strip()

            # Guardar transcripción si se especifica ruta
            if output_path:
                # Crear contenido con formato
                content = f"""================================================================================
TRANSCRIPCION DE AUDIO
================================================================================
Archivo: {os.path.basename(audio_path)}
Modelo: Whisper {model_name}
Idioma: {language}
================================================================================

{transcription_text}

================================================================================
Generado con Media Downloader - Whisper AI
================================================================================
"""
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                return True, f"Transcripción guardada en: {output_path}", transcription_text
            else:
                return True, "Transcripción completada", transcription_text

        except ImportError:
            return False, "Whisper no está instalado. Ejecuta: pip install openai-whisper", None
        except Exception as e:
            logger.exception("Transcription failed for: %s", audio_path)
            return False, f"Error en la transcripción: {str(e)}", None

    @staticmethod
    def transcribe_with_segments(audio_path, output_path=None, model_name="base", language="es"):
        """
        Transcribe un archivo de audio a texto con timestamps

        Args:
            audio_path: Ruta al archivo de audio
            output_path: Ruta donde guardar el archivo de texto (opcional)
            model_name: Modelo de Whisper a usar
            language: Idioma del audio

        Returns:
            tuple: (éxito: bool, mensaje: str, texto: str)
        """
        try:
            import whisper

            if not os.path.exists(audio_path):
                return False, f"El archivo de audio no existe: {audio_path}", None

            # Cargar modelo
            model = whisper.load_model(model_name)

            # Transcribir
            result = model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )

            # Formatear con timestamps
            lines = []
            for segment in result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()

                # Formatear tiempo
                start_str = AudioTranscriber._format_time(start)
                end_str = AudioTranscriber._format_time(end)

                lines.append(f"[{start_str} -> {end_str}] {text}")

            transcription_text = "\n".join(lines)

            # Guardar transcripción si se especifica ruta
            if output_path:
                content = f"""================================================================================
TRANSCRIPCION DE AUDIO (CON TIMESTAMPS)
================================================================================
Archivo: {os.path.basename(audio_path)}
Modelo: Whisper {model_name}
Idioma: {language}
================================================================================

{transcription_text}

================================================================================
Generado con Media Downloader - Whisper AI
================================================================================
"""
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                return True, f"Transcripción guardada en: {output_path}", transcription_text
            else:
                return True, "Transcripción completada", transcription_text

        except ImportError:
            return False, "Whisper no está instalado. Ejecuta: pip install openai-whisper", None
        except Exception as e:
            logger.exception("Segmented transcription failed for: %s", audio_path)
            return False, f"Error en la transcripción: {str(e)}", None

    @staticmethod
    def _format_time(seconds):
        """Formatea segundos a HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def get_available_models():
        """
        Obtiene la lista de modelos disponibles

        Returns:
            list: Lista de nombres de modelos
        """
        return ["tiny", "base", "small", "medium", "large"]

    @staticmethod
    def get_model_info():
        """
        Obtiene información sobre los modelos disponibles

        Returns:
            dict: Información de cada modelo
        """
        return {
            "tiny": {
                "size": "~39 MB",
                "speed": "Muy rápido",
                "quality": "Básica"
            },
            "base": {
                "size": "~74 MB",
                "speed": "Rápido",
                "quality": "Buena"
            },
            "small": {
                "size": "~244 MB",
                "speed": "Moderado",
                "quality": "Muy buena"
            },
            "medium": {
                "size": "~769 MB",
                "speed": "Lento",
                "quality": "Excelente"
            },
            "large": {
                "size": "~1550 MB",
                "speed": "Muy lento",
                "quality": "Máxima"
            }
        }
