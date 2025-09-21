import sys
import subprocess
import importlib.util

def check_and_install_packages():
    required_packages = {
        'customtkinter': 'customtkinter>=5.2.2',
        'requests': 'requests>=2.31.0',
        'tkinter': 'tkinter>=8.6'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        if importlib.util.find_spec(package) is None:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("Gerekli paketler yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools", "packaging"])
        for package in missing_packages:
            print(f"Yükleniyor: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        print("Tüm paketler başarıyla yüklendi!")

try:
    check_and_install_packages()
except Exception as e:
    print(f"Paket yükleme hatası: {e}")
    print("Lütfen internet bağlantınızı kontrol edin.")
    input("Devam etmek için Enter'a basın...")

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import json
import os
import platform
import threading
import subprocess
import zipfile
import shutil
import glob
import time
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MinecraftServerInstaller:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Minecraft Server Kurulum Programı")
        self.root.geometry("800x850")
        self.root.resizable(False, False)
        
        self.install_directory = tk.StringVar()
        self.server_name = tk.StringVar(value="MyMinecraftServer")
        self.server_type = tk.StringVar(value="Paper")
        self.minecraft_version = tk.StringVar(value="1.20.1")
        self.ram_amount = tk.StringVar(value="4")
        self.server_port = tk.StringVar(value="25565")
        
        self.server_types = {
            "Paper": "https://api.papermc.io/v2/projects/paper",
            "Purpur": "https://api.purpurmc.org/v2/purpur",
            "Spigot": "https://download.getbukkit.org/spigot/",
            "Vanilla": "https://piston-meta.mojang.com/mc/game/version_manifest.json",
            "Fabric": "https://meta.fabricmc.net/v2/versions/loader",
            "Forge": "https://files.minecraftforge.net/net/minecraftforge/forge/",
            "NeoForge": "https://maven.neoforged.net/api/maven/versions/releases/net/neoforged/neoforge",
            "Quilt": "https://meta.quiltmc.org/v3/versions/loader",
            "Arclight": "https://api.github.com/repos/IzzelAliz/Arclight/releases"
        }
        
        self.versions = {
            "Paper": ["1.21.1", "1.21", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.19.4", "1.19.3", "1.19.2", "1.18.2"],
            "Purpur": ["1.21.1", "1.21", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.19.4", "1.19.3", "1.19.2", "1.18.2"],
            "Vanilla": ["1.21.1", "1.21", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.19.4", "1.19.3", "1.19.2", "1.18.2"],
            "Spigot": ["1.21.1", "1.21", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.19.4", "1.19.3", "1.19.2", "1.18.2"],
            "Fabric": ["1.21.1", "1.21", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.19.4", "1.19.3", "1.19.2", "1.18.2"],
            "Forge": ["1.21.1", "1.21", "1.20.4", "1.20.1", "1.19.4", "1.18.2"],
            "NeoForge": ["1.21.1", "1.21", "1.20.4", "1.20.1"],
            "Quilt": ["1.21.1", "1.21", "1.20.4", "1.20.1", "1.19.4", "1.18.2"],
            "Arclight": ["1.21.1", "1.21", "1.20.4", "1.20.1", "1.19.4", "1.18.2"]
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(main_frame, text="Minecraft Server Kurulum Programı", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(20, 30))
        
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(input_frame, text="Kurulum Dizini:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
        dir_frame = ctk.CTkFrame(input_frame)
        dir_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.dir_entry = ctk.CTkEntry(dir_frame, textvariable=self.install_directory, width=500)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        dir_button = ctk.CTkButton(dir_frame, text="Gözat", command=self.select_directory, width=80)
        dir_button.pack(side="right", padx=(5, 10), pady=10)
        
        ctk.CTkLabel(input_frame, text="Sunucu İsmi:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
        ctk.CTkEntry(input_frame, textvariable=self.server_name, width=540).pack(padx=20, pady=(0, 10))
        
        row1_frame = ctk.CTkFrame(input_frame)
        row1_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(row1_frame, text="Sunucu Türü:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=(10, 5))
        self.server_type_combo = ctk.CTkComboBox(row1_frame, values=list(self.server_types.keys()), 
                                               variable=self.server_type, width=250, command=self.update_versions,
                                               state="readonly")
        self.server_type_combo.pack(side="left", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(row1_frame, text="Minecraft Sürümü:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=(10, 5))
        self.version_combo = ctk.CTkComboBox(row1_frame, values=self.versions["Paper"], 
                                           variable=self.minecraft_version, width=250,
                                           state="readonly")
        self.version_combo.pack(side="right", padx=10, pady=(0, 10))
        
        row2_frame = ctk.CTkFrame(input_frame)
        row2_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(row2_frame, text="RAM (GB):", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkEntry(row2_frame, textvariable=self.ram_amount, width=250).pack(side="left", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(row2_frame, text="Port:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkEntry(row2_frame, textvariable=self.server_port, width=250).pack(side="right", padx=10, pady=(0, 10))
        
        self.progress_frame = ctk.CTkFrame(main_frame)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=500)
        self.progress_bar.pack(padx=20, pady=15)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Kurulum için hazır", 
                                       font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(0, 15))
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        self.install_button = ctk.CTkButton(button_frame, text="🎮 SUNUCU KUR", 
                                          command=self.start_installation, 
                                          font=ctk.CTkFont(size=18, weight="bold"),
                                          height=60, width=300,
                                          fg_color=("#1f538d", "#14375e"),
                                          hover_color=("#14375e", "#1f538d"))
        self.install_button.pack(pady=15)
        
        signature_label = ctk.CTkLabel(main_frame, text="Made with ❤️ by Henzy", 
                                     font=ctk.CTkFont(size=10),
                                     text_color=("#666666", "#999999"))
        signature_label.pack(pady=(5, 10))
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.install_directory.set(directory)
            
    def update_versions(self, selected_server_type):
        if selected_server_type in self.versions:
            available_versions = self.versions[selected_server_type]
            self.version_combo.configure(values=available_versions)
            self.minecraft_version.set(available_versions[0])
        else:
            self.version_combo.configure(values=["1.20.1"])
            self.minecraft_version.set("1.20.1")
            
    def update_progress(self, value, status_text):
        self.progress_bar.set(value)
        self.status_label.configure(text=status_text)
        self.root.update()
        
    def clean_filename(self, filename):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = filename.replace(' ', '_')
        filename = filename.strip('.')
        return filename if filename else "MinecraftServer"
        
    def start_installation(self):
        if not self.install_directory.get():
            messagebox.showerror("Hata", "Lütfen kurulum dizini seçin!")
            return
            
        if not self.server_name.get():
            messagebox.showerror("Hata", "Lütfen sunucu ismi girin!")
            return
            
        cleaned_name = self.clean_filename(self.server_name.get())
        if cleaned_name != self.server_name.get():
            result = messagebox.askyesno("Dosya Adı Düzeltildi", 
                                       f"Sunucu ismi geçersiz karakterler içeriyor.\n"
                                       f"Orijinal: {self.server_name.get()}\n"
                                       f"Düzeltilmiş: {cleaned_name}\n\n"
                                       f"Devam edilsin mi?")
            if not result:
                return
        self.server_name.set(cleaned_name)
            
        try:
            ram_value = int(self.ram_amount.get())
            if ram_value < 1:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Hata", "RAM değeri geçerli bir sayı olmalı (minimum 1 GB)!")
            return
            
        try:
            port_value = int(self.server_port.get())
            if port_value < 1024 or port_value > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Hata", "Port değeri 1024-65535 arasında olmalı!")
            return
            
        self.install_button.configure(state="disabled")
        
        installation_thread = threading.Thread(target=self.install_server)
        installation_thread.daemon = True
        installation_thread.start()
        
    def install_server(self):
        try:
            self.update_progress(0.05, "Kurulum başlatılıyor...")
            
            server_dir = os.path.join(self.install_directory.get(), self.server_name.get())
            os.makedirs(server_dir, exist_ok=True)
            
            self.update_progress(0.1, "Java kontrol ediliyor...")
            java_path = self.check_and_install_java(server_dir)
            
            self.update_progress(0.3, "Sunucu dosyası indiriliyor...")
            jar_file = self.download_server_jar(server_dir)
            
            self.update_progress(0.7, "EULA dosyası oluşturuluyor...")
            self.create_eula_file(server_dir)
            
            self.update_progress(0.9, "Başlatma dosyaları oluşturuluyor...")
            self.create_start_scripts(server_dir, jar_file, java_path)
            
            self.update_progress(1.0, "Kurulum tamamlandı!")
            
            messagebox.showinfo("Başarılı", f"Minecraft sunucusu başarıyla kuruldu!\nKonum: {server_dir}\nJava: {java_path}")
            
        except Exception as e:
            self.update_progress(0, f"Hata: {str(e)}")
            messagebox.showerror("Kurulum Hatası", f"Kurulum sırasında hata oluştu:\n{str(e)}")
        finally:
            self.install_button.configure(state="normal")
            
    def check_and_install_java(self, server_dir):
        version = self.minecraft_version.get()
        required_java = "21" if version.startswith("1.21") or version.startswith("1.20") else "17"
        
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                version_output = result.stderr
                if f'version "{required_java}' in version_output:
                    self.update_progress(0.2, f"Sistem Java {required_java} bulundu, kurulum atlanıyor")
                    return "java"
                elif 'version "17' in version_output or 'version "21' in version_output:
                    java_ver = "21" if 'version "21' in version_output else "17"
                    self.update_progress(0.2, f"Sistem Java {java_ver} bulundu (önerilen: {required_java})")
                    return "java"
        except:
            pass
            
        return self.install_java_system(required_java)
            
    def install_java_system(self, required_java):
        self.update_progress(0.15, f"Java {required_java} sistem genelinde kuruluyor...")
        
        try:
            choco_result = subprocess.run(['choco', '--version'], capture_output=True, text=True, timeout=10)
            if choco_result.returncode == 0:
                self.update_progress(0.18, "Chocolatey ile Java kuruluyor...")
                install_cmd = ['choco', 'install', f'openjdk{required_java}', '-y']
                result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)  # 5 dakika timeout
                if result.returncode == 0:
                    self.update_progress(0.25, f"Java {required_java} sistem genelinde kuruldu!")
                    return "java"
        except subprocess.TimeoutExpired:
            self.update_progress(0.19, "Chocolatey timeout, Winget ile deneniyor...")
        except:
            pass
            
        try:
            winget_result = subprocess.run(['winget', '--version'], capture_output=True, text=True, timeout=10)
            if winget_result.returncode == 0:
                self.update_progress(0.18, "Winget ile Java kuruluyor...")
                install_cmd = ['winget', 'install', f'EclipseAdoptium.Temurin.{required_java}.JDK', '--silent', '--accept-package-agreements', '--accept-source-agreements']
                result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)  # 5 dakika timeout
                if result.returncode == 0:
                    self.update_progress(0.25, f"Java {required_java} sistem genelinde kuruldu!")
                    return "java"
        except subprocess.TimeoutExpired:
            self.update_progress(0.19, "Winget timeout, MSI ile deneniyor...")
        except:
            pass
            
        return self.install_java_msi(required_java)
        
    def install_java_msi(self, required_java):
        self.update_progress(0.18, f"Sistem kurulumu başarısız, portable Java indiriliyor...")
        
        return self.install_java_portable(required_java)
        
    def install_java_portable(self, required_java):
        self.update_progress(0.18, f"Java {required_java} portable olarak indiriliyor...")
        
        java_dir = os.path.join(os.environ['TEMP'], f"MinecraftJava{required_java}")
        
        if platform.system() == "Windows":
            java_filename = f"OpenJDK{required_java}U-jdk_x64_windows_hotspot.zip"
            java_url = f"https://github.com/adoptium/temurin{required_java}-binaries/releases/download/jdk-{required_java}%2B35/OpenJDK{required_java}U-jdk_x64_windows_hotspot_{required_java}_35.zip"
        else:
            java_filename = f"OpenJDK{required_java}U-jdk_x64_linux_hotspot.tar.gz"
            java_url = f"https://github.com/adoptium/temurin{required_java}-binaries/releases/download/jdk-{required_java}%2B35/OpenJDK{required_java}U-jdk_x64_linux_hotspot_{required_java}_35.tar.gz"
            
        java_zip_path = os.path.join(os.environ['TEMP'], java_filename)
        
        java_executable = os.path.join(java_dir, "bin", "java.exe" if platform.system() == "Windows" else "java")
        if os.path.exists(java_executable):
            self.update_progress(0.25, f"Önceden indirilen Java {required_java} bulundu")
            return java_executable
        
        try:
            self.update_progress(0.19, f"Java {required_java} indiriliyor...")
            response = requests.get(java_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            start_time = time.time()
            
            with open(java_zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1048576):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = 0.19 + (downloaded / total_size) * 0.05
                            elapsed = time.time() - start_time
                            if elapsed > 0:
                                speed_mbps = (downloaded / 1024 / 1024) / elapsed
                                self.update_progress(progress, f"Java indiriliyor... {speed_mbps:.1f}MB/s")
                            
            self.update_progress(0.24, "Java çıkarılıyor...")
            
            if java_filename.endswith('.zip'):
                with zipfile.ZipFile(java_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.environ['TEMP'])
                    
                extracted_folders = [f for f in os.listdir(os.environ['TEMP']) if f.startswith('jdk')]
                if extracted_folders:
                    extracted_folder = extracted_folders[0]
                    old_path = os.path.join(os.environ['TEMP'], extracted_folder)
                    if old_path != java_dir:
                        if os.path.exists(java_dir):
                            shutil.rmtree(java_dir)
                        shutil.move(old_path, java_dir)
            
            if os.path.exists(java_zip_path):
                os.remove(java_zip_path)
            
            if os.path.exists(java_executable):
                self.update_progress(0.25, f"Java {required_java} portable olarak kuruldu!")
                return java_executable
            else:
                raise Exception("Java kurulumu başarısız")
                
        except Exception as e:
            raise Exception(f"Java portable kurulumu başarısız: {str(e)}")
            
    def find_java_installation(self, version):
        possible_paths = [
            f"C:\\Program Files\\Eclipse Adoptium\\jdk-{version}*\\bin\\java.exe",
            f"C:\\Program Files\\Java\\jdk-{version}*\\bin\\java.exe",
            f"C:\\Program Files (x86)\\Eclipse Adoptium\\jdk-{version}*\\bin\\java.exe",
            f"C:\\Program Files (x86)\\Java\\jdk-{version}*\\bin\\java.exe"
        ]
        
        for pattern in possible_paths:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        return None
            
    def download_server_jar(self, server_dir):
        server_type = self.server_type.get()
        version = self.minecraft_version.get()
        
        jar_filename = f"{server_type}-{version}.jar"
        jar_path = os.path.join(server_dir, jar_filename)
        
        if server_type == "Paper":
            url = self.get_paper_download_url(version)
        elif server_type == "Purpur":
            url = self.get_purpur_download_url(version)
        elif server_type == "Vanilla":
            url = self.get_vanilla_download_url(version)
        elif server_type == "Arclight":
            url = self.get_arclight_download_url(version)
        elif server_type == "Spigot":
            url = self.get_spigot_download_url(version)
        elif server_type == "Fabric":
            url = self.get_fabric_download_url(version)
        elif server_type == "Forge":
            url = self.get_forge_download_url(version)
        elif server_type == "NeoForge":
            url = self.get_neoforge_download_url(version)
        elif server_type == "Quilt":
            url = self.get_quilt_download_url(version)
        else:
            raise Exception(f"Desteklenmeyen sunucu türü: {server_type}")
            
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        start_time = time.time()
        
        with open(jar_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1048576):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = 0.3 + (downloaded / total_size) * 0.4
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed_mbps = (downloaded / 1024 / 1024) / elapsed
                            eta_seconds = (total_size - downloaded) / (downloaded / elapsed) if downloaded > 0 else 0
                            self.update_progress(progress, f"Sunucu indiriliyor... {downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB ({speed_mbps:.1f}MB/s) ETA: {int(eta_seconds)}s")
                        
        return jar_filename
        
    def get_paper_download_url(self, version):
        builds_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
        response = requests.get(builds_url)
        response.raise_for_status()
        builds_data = response.json()
        
        latest_build = builds_data['builds'][-1]
        download_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
        return download_url
        
    def get_purpur_download_url(self, version):
        builds_url = f"https://api.purpurmc.org/v2/purpur/{version}"
        response = requests.get(builds_url)
        response.raise_for_status()
        builds_data = response.json()
        
        latest_build = builds_data['builds']['latest']
        download_url = f"https://api.purpurmc.org/v2/purpur/{version}/{latest_build}/download"
        return download_url
        
    def get_vanilla_download_url(self, version):
        manifest_response = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest.json")
        manifest_response.raise_for_status()
        manifest = manifest_response.json()
        
        version_info = None
        for v in manifest['versions']:
            if v['id'] == version:
                version_info = v
                break
                
        if not version_info:
            raise Exception(f"Sürüm bulunamadı: {version}")
            
        version_response = requests.get(version_info['url'])
        version_response.raise_for_status()
        version_data = version_response.json()
        
        return version_data['downloads']['server']['url']
        
    def get_arclight_download_url(self, version):
        releases_response = requests.get("https://api.github.com/repos/IzzelAliz/Arclight/releases")
        releases_response.raise_for_status()
        releases = releases_response.json()
        
        # Sürüm eşleşmesi ara
        for release in releases:
            has_version_asset = False
            for asset in release['assets']:
                if version in asset['name']:
                    has_version_asset = True
                    break
            
            if has_version_asset:
                for asset in release['assets']:
                    asset_name = asset['name']
                    if ('arclight' in asset_name.lower() and 
                        'neoforge' in asset_name.lower() and
                        asset_name.endswith('.jar') and 
                        'sources' not in asset_name.lower() and
                        'installer' not in asset_name.lower()):
                        return asset['browser_download_url']
                        
                for asset in release['assets']:
                    asset_name = asset['name']
                    if ('arclight' in asset_name.lower() and 
                        'forge' in asset_name.lower() and
                        'neoforge' not in asset_name.lower() and
                        asset_name.endswith('.jar') and 
                        'sources' not in asset_name.lower() and
                        'installer' not in asset_name.lower()):
                        return asset['browser_download_url']
                        
                for asset in release['assets']:
                    asset_name = asset['name']
                    if ('arclight' in asset_name.lower() and 
                        'fabric' in asset_name.lower() and
                        asset_name.endswith('.jar') and 
                        'sources' not in asset_name.lower() and
                        'installer' not in asset_name.lower()):
                        return asset['browser_download_url']
                        
        raise Exception(f"Arclight sürümü bulunamadı: {version}. Lütfen manuel olarak indirin: https://github.com/IzzelAliz/Arclight/releases")
        
    def get_spigot_download_url(self, version):
        try:
            builds_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
            response = requests.get(builds_url, timeout=10)
            if response.status_code == 200:
                builds_data = response.json()
                latest_build = builds_data['builds'][-1]
                paper_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
                return paper_url
        except:
            pass
            
        spigot_sources = [
            f"https://cdn.getbukkit.org/spigot/spigot-{version}.jar",
            f"https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar"
        ]
        
        for url in spigot_sources:
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    return url
            except:
                continue
                
        raise Exception(f"Spigot sürümü bulunamadı: {version}. Paper alternatifi kullanılıyor.")
        
    def get_fabric_download_url(self, version):
        try:
            loader_url = f"https://meta.fabricmc.net/v2/versions/loader/{version}"
            response = requests.get(loader_url, timeout=10)
            response.raise_for_status()
            loaders = response.json()
            
            if loaders:
                stable_loader = None
                for loader in loaders:
                    if loader['loader']['stable']:
                        stable_loader = loader['loader']['version']
                        break
                
                if not stable_loader:
                    stable_loader = loaders[0]['loader']['version']
                
                installer_url = "https://meta.fabricmc.net/v2/versions/installer"
                installer_response = requests.get(installer_url, timeout=10)
                installer_response.raise_for_status()
                installers = installer_response.json()
                
                if installers:
                    installer_version = installers[0]['version']
                    fabric_url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{stable_loader}/{installer_version}/server/jar"
                    return fabric_url
                    
        except Exception as e:
            pass
            
        try:
            fabric_launcher_url = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar"
            response = requests.head(fabric_launcher_url, timeout=10)
            if response.status_code == 200:
                return fabric_launcher_url
        except:
            pass
            
        raise Exception(f"Fabric sürümü bulunamadı: {version}. Lütfen manuel olarak indirin: https://fabricmc.net/use/server/")
            
    def get_forge_download_url(self, version):
        raise Exception("Forge indirme işlemi manuel olarak yapılmalıdır. Lütfen https://files.minecraftforge.net adresini ziyaret edin.")
        
    def get_neoforge_download_url(self, version):
        try:
            releases_url = "https://api.github.com/repos/neoforged/NeoForge/releases"
            response = requests.get(releases_url, timeout=10)
            if response.status_code == 200:
                releases = response.json()
                
                for release in releases:
                    tag_name = release['tag_name']
                    if version in tag_name or any(version in asset['name'] for asset in release['assets']):
                        for asset in release['assets']:
                            asset_name = asset['name']
                            if ('installer' in asset_name.lower() and 
                                asset_name.endswith('.jar') and
                                'sources' not in asset_name.lower()):
                                return asset['browser_download_url']
                                
                if releases:
                    latest_release = releases[0]
                    for asset in latest_release['assets']:
                        asset_name = asset['name']
                        if ('installer' in asset_name.lower() and 
                            asset_name.endswith('.jar') and
                            'sources' not in asset_name.lower()):
                            return asset['browser_download_url']
        except:
            pass
            
        try:
            metadata_url = "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml"
            response = requests.get(metadata_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                if '<latest>' in content:
                    start = content.find('<latest>') + 8
                    end = content.find('</latest>')
                    latest_version = content[start:end]
                    neoforge_url = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{latest_version}/neoforge-{latest_version}-installer.jar"
                    return neoforge_url
        except:
            pass
            
        raise Exception(f"NeoForge sürümü bulunamadı: {version}. Lütfen manuel olarak indirin: https://neoforged.net/")
        
    def get_quilt_download_url(self, version):
        try:
            loader_url = f"https://meta.quiltmc.org/v3/versions/loader/{version}"
            response = requests.get(loader_url, timeout=10)
            response.raise_for_status()
            loaders = response.json()
            
            if loaders:
                latest_loader = loaders[0]['loader']['version']
                
                installer_url = "https://meta.quiltmc.org/v3/versions/installer"
                installer_response = requests.get(installer_url, timeout=10)
                installer_response.raise_for_status()
                installers = installer_response.json()
                
                if installers:
                    installer_version = installers[0]['version']
                    quilt_url = f"https://meta.quiltmc.org/v3/versions/loader/{version}/{latest_loader}/{installer_version}/server/jar"
                    return quilt_url
                    
        except Exception as e:
            pass
            
        try:
            quilt_installer_url = "https://maven.quiltmc.org/repository/release/org/quiltmc/quilt-installer/1.0.0/quilt-installer-1.0.0.jar"
            response = requests.head(quilt_installer_url, timeout=10)
            if response.status_code == 200:
                return quilt_installer_url
        except:
            pass
            
        raise Exception(f"Quilt sürümü bulunamadı: {version}. Lütfen manuel olarak indirin: https://quiltmc.org/en/install/server/")
        
    def create_eula_file(self, server_dir):
        eula_path = os.path.join(server_dir, "eula.txt")
        with open(eula_path, 'w') as f:
            f.write("eula=true\n")
            
    def create_start_scripts(self, server_dir, jar_filename, java_path):
        ram_amount = self.ram_amount.get()
        
        if platform.system() == "Windows":
            bat_content = f"""@echo off
title {self.server_name.get()}
"{java_path}" -Xmx{ram_amount}G -Xms{ram_amount}G -jar {jar_filename} nogui
pause"""
            
            bat_path = os.path.join(server_dir, "start.bat")
            with open(bat_path, 'w') as f:
                f.write(bat_content)
                
        sh_content = f"""#!/bin/bash
"{java_path}" -Xmx{ram_amount}G -Xms{ram_amount}G -jar {jar_filename} nogui"""
        
        sh_path = os.path.join(server_dir, "start.sh")
        with open(sh_path, 'w') as f:
            f.write(sh_content)
            
        if platform.system() != "Windows":
            os.chmod(sh_path, 0o755)
            
        server_properties_content = f"""server-port={self.server_port.get()}
motd={self.server_name.get()}
max-players=20
online-mode=false
difficulty=normal
gamemode=survival
pvp=true
spawn-protection=16
level-name=world
enable-command-block=false"""
        
        properties_path = os.path.join(server_dir, "server.properties")
        with open(properties_path, 'w') as f:
            f.write(server_properties_content)
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MinecraftServerInstaller()
    app.run()
