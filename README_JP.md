<p align="center">
  <img src="assets/header.png" width="100%" />
</p>

<h1 align="center">FreeCAD MCP (Model Control Protocol)</h1>

<p align="center">
  <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://www.freecad.org"><img src="https://img.shields.io/badge/FreeCAD-000000?style=for-the-badge&logo=freecad&logoColor=white" alt="FreeCAD"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
   <a href="README_JP.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
   <a href="README.md"><img src="https://img.shields.io/badge/english-document-white.svg" alt="EN doc"></a>
</p>

## 🌟 概要

FreeCAD MCP (Model Control Protocol)は、サーバー-クライアントアーキテクチャを通じてFreeCADと対話するためのシンプルなインターフェースを提供します。これにより、コマンドの実行や現在のFreeCADドキュメントとシーンに関する情報の取得が可能になります。

https://github.com/user-attachments/assets/5acafa17-4b5b-4fef-9f6c-617e85357d44

## ⚙️ 設定

MCPサーバーの設定には、以下のようなJSON形式を使用します：

```json
{
    "mcpServers": {
        "freecad": {
            "command": "C:\\ProgramData\\anaconda3\\python.exe",
            "args": [
                "C:\\Users\\USER\\AppData\\Roaming\\FreeCAD\\Mod\\freecad_mcp\\src\\freecad_bridge.py"
            ]
        }
    }
}
```

### 設定の詳細

- **command**: FreeCAD MCPサーバーを実行するPython実行ファイルのパス。OSによって異なります：
  - **Windows**: 通常は `C:\\ProgramData\\anaconda3\\python.exe` や `C:\\Python39\\python.exe` など
  - **Linux**: `/usr/bin/python3` またはPythonインストールパス
  - **macOS**: 通常は `/usr/local/bin/python3` またはPythonインストールパス

- **args**: Pythonコマンドに渡す引数の配列。最初の引数は `freecad_bridge.py` スクリプトへのパスで、MCPサーバーのロジックを処理します。インストール先に応じてパスを調整してください。

### 各OSでの設定例

#### Windows
```json
{
    "mcpServers": {
        "freecad": {
            "command": "C:\\ProgramData\\anaconda3\\python.exe",
            "args": [
                "C:\\Users\\USER\\AppData\\Roaming\\FreeCAD\\Mod\\freecad_mcp\\src\\freecad_bridge.py"
            ]
        }
    }
}
```

#### Linux
```json
{
    "mcpServers": {
        "freecad": {
            "command": "/usr/bin/python3",
            "args": [
                "/home/USER/.FreeCAD/Mod/freecad_mcp/src/freecad_bridge.py"
            ]
        }
    }
}
```

#### macOS
```json
{
    "mcpServers": {
        "freecad": {
            "command": "/usr/local/bin/python3",
            "args": [
                "/Users/USER/Library/Preferences/FreeCAD/Mod/freecad_mcp/src/freecad_bridge.py"
            ]
        }
    }
}
```

## 🚀 機能

FreeCAD MCPは現在、以下の機能をサポートしています：

### 1. `get_scene_info`

現在のFreeCADドキュメントに関する包括的な情報を取得します：
- ドキュメントのプロパティ（名前、ラベル、ファイル名、オブジェクト数）
- 詳細なオブジェクト情報（タイプ、位置、回転、形状プロパティ）
- スケッチデータ（ジオメトリ、拘束）
- ビュー情報（カメラ位置、方向など）

### 2. `run_script`

FreeCADコンテキスト内で任意のPythonコードを実行します。これにより、複雑な操作、新しいオブジェクトの作成、既存オブジェクトの変更、タスクの自動化などがFreeCADのPython APIを使用して実行できます。

### 使用例

FreeCAD MCPを使用するには、以下のようにサーバーに接続してコマンドを送信します：

```python
import socket
import json

# FreeCAD MCPサーバーに接続
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9876))

# シーン情報を取得する例
command = {
    "type": "get_scene_info"
}
client.sendall(json.dumps(command).encode('utf-8'))

# レスポンスを受信
response = client.recv(4096)
print(json.loads(response.decode('utf-8')))

# スクリプトを実行する例
script = """
import FreeCAD
doc = FreeCAD.ActiveDocument
box = doc.addObject("Part::Box", "MyBox")
box.Length = 20
box.Width = 20
box.Height = 20
doc.recompute()
"""
command = {
    "type": "run_script",
    "params": {
        "script": script
    }
}
client.sendall(json.dumps(command).encode('utf-8'))

# レスポンスを受信
response = client.recv(4096)
print(json.loads(response.decode('utf-8')))

# 接続を閉じる
client.close()
```

## 🔧 インストール

1. リポジトリをクローンまたはファイルをダウンロードします。
2. 必要なPythonパッケージをインストールします：
   ```bash
   pip install mcp
   ```
3. `freecad_mcp`ディレクトリをFreeCADモジュールディレクトリに配置します：
   - Windows: `%APPDATA%/FreeCAD/Mod/`
   - Linux: `~/.FreeCAD/Mod/`
   - macOS: `~/Library/Preferences/FreeCAD/Mod/`
4. Python実行ファイルのパスを確認します：
   - Windows: コマンドプロンプトで`where python`を実行
   - Linux/macOS: ターミナルで`which python3`を実行
   設定ファイルの`command`設定にこのパスを使用します。
5. FreeCADを再起動し、ワークベンチセレクターから「FreeCAD MCP」を選択します。

## 👥 コントリビューション

イシューやプルリクエストの提出を歓迎します！フィードバックや貢献をお待ちしています。

## 📝 ライセンス

このプロジェクトはMITライセンスの下で提供されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
