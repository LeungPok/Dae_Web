import os
import shutil
import subprocess
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File
from fastapi.responses import HTMLResponse, FileResponse  # 【新增】FileResponse
from pydantic import BaseModel

CONFIG_PATH = "/etc/dae/config.dae"
BACKUP_DIR = "/etc/dae/backups"

app = FastAPI(title="DAE Admin Dashboard")

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR, exist_ok=True)


class ConfigModel(BaseModel):
    content: str


def cleanup_backups(keep=10):
    try:
        files = os.listdir(BACKUP_DIR)
        backups = [f for f in files if f.startswith("config.") and f.endswith(".dae")]
        backups.sort()
        if len(backups) > keep:
            to_delete = backups[:-keep]
            for f in to_delete:
                os.remove(os.path.join(BACKUP_DIR, f))
    except Exception as e:
        print(f"清理备份失败: {e}")


@app.get("/api/status")
def get_status():
    try:
        systemctl_bin = shutil.which("systemctl") or "/bin/systemctl"
        result = subprocess.run([systemctl_bin, "is-active", "dae"], capture_output=True, text=True)
        return {"active": result.stdout.strip() == "active"}
    except Exception:
        return {"active": False}


@app.get("/api/config")
def get_config():
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(status_code=404, detail="未找到配置文件")
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取失败: {str(e)}")


# 【修改】保存配置不再自动备份
@app.post("/api/config/save")
def save_config(config: ConfigModel):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(config.content)
        return {"status": "success", "message": "保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


# 【新增】手动创建备份接口
@app.post("/api/backups/create")
def create_backup():
    try:
        if not os.path.exists(CONFIG_PATH):
            raise HTTPException(status_code=404, detail="配置文件不存在，无法备份")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"config.{timestamp}.dae")
        shutil.copy2(CONFIG_PATH, backup_path)

        cleanup_backups(10)  # 触发清理
        return {"status": "success", "message": f"已创建备份: config.{timestamp}.dae"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"备份失败: {str(e)}")


# 【新增】下载备份文件接口
@app.get("/api/backups/download/{filename}")
def download_backup(filename: str):
    file_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(
        path=file_path,
        media_type='application/octet-stream',
        filename=filename
    )


@app.post("/api/config/reload")
def reload_dae():
    try:
        dae_bin = shutil.which("dae") or "/usr/bin/dae"
        result = subprocess.run([dae_bin, "reload"], capture_output=True, text=True, check=True)
        return {"status": "success", "message": "重载成功", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"重载失败: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统错误: {str(e)}")


@app.get("/api/backups")
def list_backups():
    try:
        files = os.listdir(BACKUP_DIR)
        backups = [f for f in files if f.startswith("config.") and f.endswith(".dae")]
        backups.sort(reverse=True)
        return {"backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备份列表失败: {str(e)}")


@app.post("/api/backups/restore/{filename}")
def restore_backup(filename: str):
    backup_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(backup_path):
        raise HTTPException(status_code=404, detail="备份文件不存在")
    try:
        if os.path.exists(CONFIG_PATH):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_before_restore")
            shutil.copy2(CONFIG_PATH, os.path.join(BACKUP_DIR, f"config.{timestamp}.dae"))

        shutil.copy2(backup_path, CONFIG_PATH)
        cleanup_backups(10)
        return {"status": "success", "message": f"成功恢复至版本: {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    journalctl_bin = shutil.which("journalctl") or "/usr/bin/journalctl"
    process = await asyncio.create_subprocess_exec(
        journalctl_bin, "-u", "dae", "-f", "-n", "100",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(line.decode("utf-8", errors="ignore"))
    except WebSocketDisconnect:
        pass
    finally:
        try:
            process.terminate()
        except:
            pass


@app.get("/", response_class=HTMLResponse)
def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
