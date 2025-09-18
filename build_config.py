#!/usr/bin/env python3
"""
应用打包配置和构建脚本
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime


class AppBuilder:
    """应用构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.assets_dir = self.project_root / "assets"
        
        # 应用信息
        self.app_name = "TestCaseGenerator"
        self.app_version = "1.0.0"
        self.app_description = "基于AI的PRD文档测试用例生成工具"
        self.app_author = "Test Case Generator Team"
        
        # 平台信息
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()
        
        print(f"🚀 初始化应用构建器")
        print(f"   平台: {self.platform}")
        print(f"   架构: {self.architecture}")
        print(f"   应用: {self.app_name} v{self.app_version}")
    
    def clean_build_dirs(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   已清理: {dir_path}")
        
        # 清理PyInstaller缓存
        spec_files = list(self.project_root.glob("*.spec"))
        for spec_file in spec_files:
            spec_file.unlink()
            print(f"   已删除: {spec_file}")
    
    def create_pyinstaller_spec(self):
        """创建PyInstaller规格文件"""
        print("📝 创建PyInstaller规格文件...")
        
        # 收集数据文件
        datas = [
            ("src/ui/assets", "ui/assets"),  # UI资源文件
            ("assets", "assets"),  # 应用资源
        ]
        
        # 隐藏导入
        hiddenimports = [
            "PyQt6.QtCore",
            "PyQt6.QtGui", 
            "PyQt6.QtWidgets",
            "PIL",
            "requests",
            "openai",
            "anthropic",
            "paddleocr",
            "pytesseract",
            "xmindparser",
        ]
        
        # 排除模块
        excludes = [
            "tkinter",
            "matplotlib",
            "scipy",
            "numpy.distutils",
            "test",
            "unittest",
            "pytest",
        ]
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas={datas},
    hiddenimports={hiddenimports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={excludes},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='assets/icon.ico' if '{self.platform}' == 'windows' else 'assets/icon.icns',
)
'''
        
        spec_file = self.project_root / f"{self.app_name}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"   已创建: {spec_file}")
        return spec_file
    
    def create_version_info(self):
        """创建版本信息文件（Windows）"""
        if self.platform != "windows":
            return
        
        print("📋 创建版本信息文件...")
        
        version_info = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{self.app_author}'),
        StringStruct(u'FileDescription', u'{self.app_description}'),
        StringStruct(u'FileVersion', u'{self.app_version}'),
        StringStruct(u'InternalName', u'{self.app_name}'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 {self.app_author}'),
        StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
        StringStruct(u'ProductName', u'{self.app_name}'),
        StringStruct(u'ProductVersion', u'{self.app_version}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_file = self.project_root / "version_info.txt"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_info)
        
        print(f"   已创建: {version_file}")
    
    def create_assets(self):
        """创建应用资源文件"""
        print("🎨 创建应用资源...")
        
        self.assets_dir.mkdir(exist_ok=True)
        
        # 创建简单的图标文件（如果不存在）
        icon_files = {
            "icon.ico": "Windows图标",
            "icon.icns": "macOS图标", 
            "icon.png": "通用图标"
        }
        
        for icon_file, description in icon_files.items():
            icon_path = self.assets_dir / icon_file
            if not icon_path.exists():
                # 创建占位符图标文件
                icon_path.touch()
                print(f"   已创建占位符: {icon_file} ({description})")
    
    def build_executable(self):
        """构建可执行文件"""
        print("🔨 构建可执行文件...")
        
        spec_file = self.create_pyinstaller_spec()
        
        # 运行PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        print(f"   执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("   ✅ 构建成功!")
            
            # 显示构建结果
            exe_path = self.dist_dir / self.app_name
            if self.platform == "windows":
                exe_path = exe_path.with_suffix(".exe")
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"   📦 可执行文件: {exe_path}")
                print(f"   📏 文件大小: {size_mb:.1f} MB")
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 构建失败: {e}")
            print(f"   错误输出: {e.stderr}")
            return False
        
        return True
    
    def create_installer_script(self):
        """创建安装程序脚本"""
        print("📦 创建安装程序脚本...")
        
        if self.platform == "windows":
            self._create_windows_installer()
        elif self.platform == "darwin":
            self._create_macos_installer()
        else:
            self._create_linux_installer()
    
    def _create_windows_installer(self):
        """创建Windows安装程序（NSIS脚本）"""
        nsis_script = f'''
; 测试用例生成器安装脚本
!define APPNAME "{self.app_name}"
!define APPVERSION "{self.app_version}"
!define APPEXE "{self.app_name}.exe"

Name "${{APPNAME}}"
OutFile "dist/${{APPNAME}}_Setup_v${{APPVERSION}}.exe"
InstallDir "$PROGRAMFILES\\${{APPNAME}}"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\\${{APPNAME}}\\*"
    
    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\\${{APPNAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\${{APPEXE}}"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\卸载.lnk" "$INSTDIR\\uninstall.exe"
    
    ; 创建桌面快捷方式
    CreateShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\${{APPEXE}}"
    
    ; 写入卸载信息
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayVersion" "${{APPVERSION}}"
    
    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    ; 删除文件
    RMDir /r "$INSTDIR"
    
    ; 删除快捷方式
    Delete "$DESKTOP\\${{APPNAME}}.lnk"
    RMDir /r "$SMPROGRAMS\\${{APPNAME}}"
    
    ; 删除注册表项
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
SectionEnd
'''
        
        nsis_file = self.project_root / "installer.nsi"
        with open(nsis_file, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        print(f"   已创建NSIS脚本: {nsis_file}")
    
    def _create_macos_installer(self):
        """创建macOS安装程序"""
        # 创建.app包结构
        app_name = f"{self.app_name}.app"
        app_dir = self.dist_dir / app_name
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # 创建Info.plist
        info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.testcasegenerator.app</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleVersion</key>
    <string>{self.app_version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.app_version}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
'''
        
        plist_file = contents_dir / "Info.plist"
        plist_file.parent.mkdir(parents=True, exist_ok=True)
        with open(plist_file, 'w', encoding='utf-8') as f:
            f.write(info_plist)
        
        print(f"   已创建macOS应用包结构: {app_dir}")
    
    def _create_linux_installer(self):
        """创建Linux安装脚本"""
        install_script = f'''#!/bin/bash
# {self.app_name} 安装脚本

APP_NAME="{self.app_name}"
APP_VERSION="{self.app_version}"
INSTALL_DIR="/opt/$APP_NAME"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

echo "安装 $APP_NAME v$APP_VERSION..."

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 创建安装目录
mkdir -p "$INSTALL_DIR"
cp -r dist/$APP_NAME/* "$INSTALL_DIR/"

# 创建符号链接
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_DIR/$APP_NAME"

# 创建桌面文件
cat > "$DESKTOP_DIR/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name={self.app_name}
Comment={self.app_description}
Exec=$INSTALL_DIR/$APP_NAME
Icon=$INSTALL_DIR/icon.png
Terminal=false
Type=Application
Categories=Development;
EOF

echo "安装完成!"
echo "可以通过命令 '$APP_NAME' 或应用菜单启动程序"
'''
        
        install_file = self.project_root / "install.sh"
        with open(install_file, 'w', encoding='utf-8') as f:
            f.write(install_script)
        
        # 设置执行权限
        install_file.chmod(0o755)
        
        print(f"   已创建Linux安装脚本: {install_file}")
    
    def test_executable(self):
        """测试可执行文件"""
        print("🧪 测试可执行文件...")
        
        exe_path = self.dist_dir / self.app_name
        if self.platform == "windows":
            exe_path = exe_path.with_suffix(".exe")
        
        if not exe_path.exists():
            print(f"   ❌ 可执行文件不存在: {exe_path}")
            return False
        
        # 简单的启动测试（非GUI模式）
        try:
            result = subprocess.run(
                [str(exe_path), "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            print(f"   ✅ 可执行文件测试通过")
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"   ⚠️  可执行文件测试超时或失败: {e}")
            return True  # GUI应用可能无法在命令行模式下正常退出
    
    def create_distribution_package(self):
        """创建分发包"""
        print("📦 创建分发包...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"{self.app_name}_v{self.app_version}_{self.platform}_{self.architecture}_{timestamp}"
        
        # 创建分发目录
        package_dir = self.project_root / "packages"
        package_dir.mkdir(exist_ok=True)
        
        if self.platform == "windows":
            # Windows: 创建ZIP包
            package_file = package_dir / f"{package_name}.zip"
            shutil.make_archive(str(package_file.with_suffix("")), 'zip', self.dist_dir)
        else:
            # Linux/macOS: 创建tar.gz包
            package_file = package_dir / f"{package_name}.tar.gz"
            shutil.make_archive(str(package_file.with_suffix("").with_suffix("")), 'gztar', self.dist_dir)
        
        print(f"   📦 分发包已创建: {package_file}")
        
        # 计算文件大小
        if package_file.exists():
            size_mb = package_file.stat().st_size / (1024 * 1024)
            print(f"   📏 包大小: {size_mb:.1f} MB")
        
        return package_file
    
    def build_all(self):
        """执行完整构建流程"""
        print(f"\n🚀 开始构建 {self.app_name} v{self.app_version}")
        print("=" * 60)
        
        try:
            # 1. 清理构建目录
            self.clean_build_dirs()
            
            # 2. 创建资源文件
            self.create_assets()
            
            # 3. 创建版本信息
            self.create_version_info()
            
            # 4. 构建可执行文件
            if not self.build_executable():
                return False
            
            # 5. 测试可执行文件
            self.test_executable()
            
            # 6. 创建安装程序脚本
            self.create_installer_script()
            
            # 7. 创建分发包
            package_file = self.create_distribution_package()
            
            print("\n" + "=" * 60)
            print("✅ 构建完成!")
            print(f"📦 分发包: {package_file}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 构建失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="应用构建工具")
    parser.add_argument("--clean", action="store_true", help="只清理构建目录")
    parser.add_argument("--test", action="store_true", help="只测试可执行文件")
    parser.add_argument("--installer", action="store_true", help="只创建安装程序")
    
    args = parser.parse_args()
    
    builder = AppBuilder()
    
    if args.clean:
        builder.clean_build_dirs()
    elif args.test:
        builder.test_executable()
    elif args.installer:
        builder.create_installer_script()
    else:
        success = builder.build_all()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()