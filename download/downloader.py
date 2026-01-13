#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lógica de descarga de vídeos de YouTube
"""

import os
import yt_dlp
from config import AUDIO_QUALITY, AUDIO_CODEC


class YouTubeDownloader:
    """Clase para manejar las descargas de YouTube"""
    
    @staticmethod
    def get_audio_options(output_path):
        """
        Obtiene las opciones de configuración para descargar solo audio
        
        Args:
            output_path: Ruta completa del archivo o carpeta donde guardar
            
        Returns:
            dict: Opciones de configuración para yt-dlp
        """
        # Si es un archivo completo, usarlo directamente; si no, añadir template
        if os.path.splitext(output_path)[1]:
            output_template = output_path
        else:
            output_template = os.path.join(output_path, "%(title)s.%(ext)s")
        
        return {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': AUDIO_CODEC,
                'preferredquality': AUDIO_QUALITY,
            }],
            'quiet': False,
            'no_warnings': False,
        }
    
    @staticmethod
    def get_video_format_selector(quality):
        """
        Obtiene el selector de formato según la calidad elegida
        
        Args:
            quality: Calidad seleccionada (str)
            
        Returns:
            str: Selector de formato para yt-dlp
        """
        format_selectors = {
            "Mejor calidad disponible": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
            "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
            "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best",
            "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best",
            "240p": "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[height<=240][ext=mp4]/best"
        }
        
        return format_selectors.get(quality, format_selectors["Mejor calidad disponible"])
    
    @staticmethod
    def get_video_options(output_path, quality):
        """
        Obtiene las opciones de configuración para descargar vídeo
        
        Args:
            output_path: Ruta completa del archivo o carpeta donde guardar
            quality: Calidad seleccionada (str)
            
        Returns:
            dict: Opciones de configuración para yt-dlp
        """
        # Si es un archivo completo, usarlo directamente; si no, añadir template
        if os.path.splitext(output_path)[1]:
            output_template = output_path
        else:
            output_template = os.path.join(output_path, "%(title)s.%(ext)s")
        format_selector = YouTubeDownloader.get_video_format_selector(quality)
        
        return {
            'format': format_selector,
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
        }
    
    @staticmethod
    def get_download_options(output_folder, is_audio, quality=None):
        """
        Obtiene las opciones de configuración según el formato elegido
        
        Args:
            output_folder: Carpeta donde guardar el archivo
            is_audio: True si es solo audio, False si es vídeo
            quality: Calidad del vídeo (solo si is_audio=False)
            
        Returns:
            dict: Opciones de configuración para yt-dlp
        """
        if is_audio:
            return YouTubeDownloader.get_audio_options(output_folder)
        else:
            return YouTubeDownloader.get_video_options(output_folder, quality)
    
    @staticmethod
    def get_video_info(url):
        """
        Obtiene información del vídeo sin descargarlo
        
        Args:
            url: URL del vídeo de YouTube
            
        Returns:
            dict: Información del vídeo
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    
    @staticmethod
    def download(url, output_folder, is_audio, quality, progress_hook):
        """
        Descarga el vídeo o audio de YouTube
        
        Args:
            url: URL del vídeo de YouTube
            output_folder: Carpeta donde guardar el archivo
            is_audio: True si es solo audio, False si es vídeo
            quality: Calidad del vídeo (solo si is_audio=False)
            progress_hook: Hook para reportar el progreso
            
        Returns:
            tuple: (éxito: bool, mensaje: str, título: str)
        """
        try:
            ydl_opts = YouTubeDownloader.get_download_options(
                output_folder, is_audio, quality
            )
            ydl_opts['progress_hooks'] = [progress_hook.hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener información del vídeo
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video')
                
                # Descargar
                ydl.download([url])
                
                return True, "Descarga completada", video_title
        
        except Exception as e:
            error_msg = str(e)
            return False, error_msg, None
