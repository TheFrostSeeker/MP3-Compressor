#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 04/01/2025 by Franck
"""

# Imports
import os
import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import math
import threading
import logging

# Initialiser le logging pour les erreurs
logging.basicConfig(filename='mp3_compressor.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def calculate_bitrate(target_size_mb, duration):
    target_size_bytes = target_size_mb * 1024 * 1024
    target_bitrate_bps = (target_size_bytes * 8) / duration
    target_bitrate_kbps = target_bitrate_bps / 1000
    return f"{math.ceil(target_bitrate_kbps)}k"


class MP3CompressorApp:
    def __init__(self, root):
        self.compress_button = None
        self.output_file_label = None
        self.select_save_button = None
        self.target_size_entry = None
        self.target_size_label = None
        self.input_file_label = None
        self.file_size_label = None
        self.select_file_button = None
        self.root = root
        self.root.title("MP3 Compressor")
        self.root.geometry("400x350")

        # Attributs pour les fichiers
        self.input_file = None
        self.output_file = None
        self.compress_thread = None

        # Interface utilisateur
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.select_file_button = ttk.Button(frame, text="Sélectionner le fichier MP3", command=self.select_file)
        self.select_file_button.grid(row=0, column=0, pady=10, sticky="w")

        self.file_size_label = ttk.Label(frame, text="Taille du fichier : N/A")
        self.file_size_label.grid(row=1, column=0, pady=5, sticky="w")

        self.input_file_label = ttk.Label(frame, text="Chemin du fichier source : N/A")
        self.input_file_label.grid(row=2, column=0, pady=5, sticky="w")

        self.target_size_label = ttk.Label(frame, text="Taille cible (en Mo) :")
        self.target_size_label.grid(row=3, column=0, pady=5, sticky="w")

        self.target_size_entry = ttk.Entry(frame)
        self.target_size_entry.grid(row=4, column=0, pady=5, sticky="w")

        self.select_save_button = ttk.Button(frame, text="Sélectionner l'emplacement de sauvegarde", command=self.select_save_location)
        self.select_save_button.grid(row=5, column=0, pady=10, sticky="w")

        self.output_file_label = ttk.Label(frame, text="Chemin du fichier de sortie : N/A")
        self.output_file_label.grid(row=6, column=0, pady=5, sticky="w")

        self.compress_button = ttk.Button(frame, text="Compresser", command=self.compress_mp3)
        self.compress_button.grid(row=7, column=0, pady=20)

    def select_file(self):
        self.input_file = filedialog.askopenfilename(title="Sélectionnez un fichier MP3", filetypes=[("Fichiers MP3", "*.mp3")])
        if self.input_file:
            self.input_file_label.config(text=f"Chemin du fichier source : {self.input_file}")
            file_size = os.path.getsize(self.input_file)
            self.file_size_label.config(text=f"Taille du fichier : {file_size / (1024 * 1024):.2f} Mo")

    def select_save_location(self):
        self.output_file = filedialog.asksaveasfilename(title="Enregistrez sous", defaultextension=".mp3", filetypes=[("Fichiers MP3", "*.mp3")])
        if self.output_file:
            self.output_file_label.config(text=f"Chemin du fichier de sortie : {self.output_file}")

    def get_audio_duration(self):
        try:
            probe = ffmpeg.probe(self.input_file, v='error', select_streams='a:0', show_entries='stream=duration')
            duration = float(probe['streams'][0]['duration'])
            return duration
        except ffmpeg.Error as e:
            logging.error(f"Erreur lors de l'obtention de la durée du fichier : {e}")
            messagebox.showerror ("Erreur", f"Erreur lors de l'obtention de la durée du fichier : {e}")
            return None

    def compress_mp3(self):
        if not self.input_file:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier MP3.")
            return

        try:
            target_size_mb = float(self.target_size_entry.get())
            if target_size_mb <= 0:
                messagebox.showerror("Erreur", "La taille cible doit être un nombre positif.")
                return
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une taille valide.")
            return

        if not self.output_file:
            messagebox.showerror("Erreur", "Veuillez sélectionner l'emplacement pour enregistrer le fichier.")
            return

        duration = self.get_audio_duration()
        if duration is None:
            return

        target_bitrate = calculate_bitrate(target_size_mb, duration)

        self.compress_button.config(state=tk.DISABLED)  # Disable button during processing
        self.compress_thread = threading.Thread(target=self.run_compression, args=(target_bitrate,))
        self.compress_thread.start()

    def run_compression(self, target_bitrate):
        try:
            ffmpeg.input(self.input_file).output(self.output_file, audio_bitrate=target_bitrate).run(overwrite_output=True)

            compressed_file_size = os.path.getsize(self.output_file)
            compressed_size_mb = compressed_file_size / (1024 * 1024)

            messagebox.showinfo("Succès", f"Fichier compressé avec succès :\n\n"
                                          f"Taille originale : {os.path.getsize(self.input_file) / (1024 * 1024):.2f} Mo\n"
                                          f"Taille après compression : {compressed_size_mb:.2f} Mo\n"
                                          f"Enregistré sous : {self.output_file}")
            logging.info(f"Compression réussie : {self.input_file} -> {self.output_file}")
        except ffmpeg.Error as e:
            logging.error(f"Erreur lors de la compression : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la compression : {e}")
        finally:
            self.compress_button.config(state=tk.NORMAL)  # Re-enable button after processing

def main():
    root = tk.Tk()
    MP3CompressorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()