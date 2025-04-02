<h1 align="center">FreeCAD MCPソースコード</h1>

<p align="center">
   <a href="README_JP.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
   <a href="README.md"><img src="https://img.shields.io/badge/english-document-white.svg" alt="EN doc"></a>
</p>

## 🔧 コアコンポーネント

### `freecad_bridge.py`

MCPサーバーとFreeCAD間のメインブリッジコンポーネントです。

#### 関数

##### `send_to_freecad(command: Dict[str, Any]) -> Dict[str, Any]`
FreeCADとのソケット通信を処理します：
- ソケット接続の作成
- JSONフォーマットのコマンド送信
- レスポンスの受信とパース
- 接続エラーの処理

##### `@mcp.tool() send_command(command: str) -> str`
FreeCADにコマンドを送信し、ドキュメントのコンテキストを取得します：
- 指定されたコマンドの実行
- ドキュメント情報の返却
- アクティブなオブジェクトとプロパティの取得
- 現在のビュー状態の提供

##### `@mcp.tool() run_script(script: str) -> str`
FreeCADコンテキストでPythonスクリプトを実行します：
- 任意のPythonコードの実行
- 実行結果をJSONで返却
- スクリプト実行エラーの処理

#### 定数

- `FREECAD_HOST`: サーバーホスト（デフォルト: 'localhost'）
- `FREECAD_PORT`: サーバーポート（デフォルト: 9876）

#### サーバー設定

FastMCPサーバーの初期化を使用：
```python
mcp = FastMCP("freecad-bridge")
mcp.run(transport='stdio')
```
