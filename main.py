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
import math


class MP3CompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Compressor")
        self.root.geometry("400x350")  # Augmenter la taille de la fenêtre pour plus d'espace

        # Attributs pour les fichiers
        self.input_file = None
        self.output_file = None

        # Interface utilisateur
        self.create_widgets()

    def create_widgets(self):
        # Bouton pour sélectionner le fichier MP3
        self.select_file_button = tk.Button(self.root, text="Sélectionner le fichier MP3", command=self.select_file)
        self.select_file_button.pack(pady=10)

        # Label pour afficher la taille du fichier
        self.file_size_label = tk.Label(self.root, text="Taille du fichier : N/A")
        self.file_size_label.pack(pady=5)

        # Label pour afficher le chemin du fichier source
        self.input_file_label = tk.Label(self.root, text="Chemin du fichier source : N/A")
        self.input_file_label.pack(pady=5)

        # Entrée pour la taille cible (en Mo)
        self.target_size_label = tk.Label(self.root, text="Taille cible (en Mo) :")
        self.target_size_label.pack(pady=5)

        self.target_size_entry = tk.Entry(self.root)
        self.target_size_entry.pack(pady=5)

        # Bouton pour sélectionner l'emplacement de sauvegarde
        self.select_save_button = tk.Button(self.root, text="Sélectionner l'emplacement de sauvegarde",
                                            command=self.select_save_location)
        self.select_save_button.pack(pady=10)

        # Label pour afficher le chemin du fichier de sortie
        self.output_file_label = tk.Label(self.root, text="Chemin du fichier de sortie : N/A")
        self.output_file_label.pack(pady=5)

        # Bouton pour démarrer la compression
        self.compress_button = tk.Button(self.root, text="Compresser", command=self.compress_mp3)
        self.compress_button.pack(pady=20)

    def select_file(self):
        """Ouvre une fenêtre pour sélectionner un fichier MP3."""
        self.input_file = filedialog.askopenfilename(
            title="Sélectionnez un fichier MP3",
            filetypes=[("Fichiers MP3", "*.mp3")]
        )
        if self.input_file:
            # Mettre à jour le label avec le chemin du fichier sélectionné
            self.input_file_label.config(text=f"Chemin du fichier source : {self.input_file}")
            file_size = os.path.getsize(self.input_file)
            self.file_size_label.config(text=f"Taille du fichier : {file_size / (1024 * 1024):.2f} Mo")

    def select_save_location(self):
        """Ouvre une fenêtre pour sélectionner l'emplacement du fichier de sortie."""
        self.output_file = filedialog.asksaveasfilename(
            title="Enregistrez sous",
            defaultextension=".mp3",
            filetypes=[("Fichiers MP3", "*.mp3")]
        )
        if self.output_file:
            # Mettre à jour le label avec le chemin du fichier de sortie
            self.output_file_label.config(text=f"Chemin du fichier de sortie : {self.output_file}")

    def get_audio_duration(self):
        """Obtient la durée du fichier audio en secondes."""
        try:
            # Utilisation de ffmpeg pour obtenir la durée du fichier MP3
            probe = ffmpeg.probe(self.input_file, v='error', select_streams='a:0', show_entries='stream=duration')
            duration = float(probe['streams'][0]['duration'])
            return duration
        except ffmpeg.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'obtention de la durée du fichier : {e}")
            return None

    def calculate_bitrate(self, target_size_mb, duration):
        """Calcule le bitrate nécessaire pour atteindre la taille cible."""
        # Convertir la taille cible de Mo à octets
        target_size_bytes = target_size_mb * 1024 * 1024
        # Calculer le bitrate cible en bps (bits par seconde)
        target_bitrate_bps = (target_size_bytes * 8) / duration
        # Convertir en kbps (kilobits par seconde)
        target_bitrate_kbps = target_bitrate_bps / 1000
        return f"{math.ceil(target_bitrate_kbps)}k"  # Arrondi au supérieur

    def compress_mp3(self):
        """Démarre la compression du fichier MP3."""
        # Vérifier les entrées
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

        # Calculer la durée du fichier
        duration = self.get_audio_duration()
        if duration is None:
            return

        # Calculer le bitrate
        target_bitrate = self.calculate_bitrate(target_size_mb, duration)

        try:
            # Exécuter la compression avec ffmpeg
            ffmpeg.input(self.input_file).output(self.output_file, audio_bitrate=target_bitrate).run(
                overwrite_output=True)

            # Récupérer la taille du fichier après compression
            compressed_file_size = os.path.getsize(self.output_file)
            compressed_size_mb = compressed_file_size / (1024 * 1024)

            # Afficher la taille du fichier compressé dans une boîte de dialogue
            messagebox.showinfo("Succès", f"Fichier compressé avec succès :\n\n"
                                          f"Taille originale : {os.path.getsize(self.input_file) / (1024 * 1024):.2f} Mo\n"
                                          f"Taille après compression : {compressed_size_mb:.2f} Mo\n"
                                          f"Enregistré sous : {self.output_file}")
        except ffmpeg.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la compression : {e}")


def main():
    root = tk.Tk()
    app = MP3CompressorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
