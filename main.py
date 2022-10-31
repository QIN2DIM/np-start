# -*- coding: utf-8 -*-
# Time       : 2022/10/9 13:06
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import base64
import functools
import json
import logging
import os
import re
import sys
import uuid
from dataclasses import dataclass

# 阻止 python2 及非 linux 系统运行
if sys.version_info[0] < 3 or sys.platform != "linux":
    sys.exit()
os.system("clear")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
)

WORKSPACE = "/home/naiveproxy"
PATH_CADDY = os.path.join(WORKSPACE, "caddy")

CADDYFILE_TEMPLATE = """
:443, [domain]
tls [email]
route {
  forward_proxy {
   basic_auth [username] [password]
   hide_ip
   hide_via
   probe_resistance
  }
  reverse_proxy https://demo.cloudreve.org   {
   header_up  Host  {upstream_hostport}
   header_up  X-Forwarded-Host  {host}
  }
}
"""

V2RAYN_TEMPLATE = """
{
    "listen": "socks://127.0.0.1:58185",
    "proxy": "[proxy]"
}
"""

GUIDER_PANEL = """
 -------------------------------------------
|**********       np-start         **********|
|**********    Author: QIN2DIM     **********|
|**********     Version: 0.0.5     **********|
 -------------------------------------------
Tips:np-start 命令再次运行本脚本.
.............................................

############################### 

..................... 
1)  敏捷部署 Naiveproxy 
2)  卸载 
..................... 
3)  启动 
4)  暂停 
5)  重新启动 
6)  运行状态 
..................... 
7)  查看当前配置 
8)  重新配置

############################### 



0)退出 
............................................. 
请选择: """


@dataclass
class CaddyServer:
    username: str = f"{uuid.uuid4().hex}"[:8]
    password: str = uuid.uuid4().hex
    email: str = f"{str(uuid.uuid4().hex)[:8]}@tesla.com"
    domain: str = ""
    port: str = "443"
    scheme: str = "https"  # "https" or "quic"

    def get_caddyfile(self):
        caddyfile = CADDYFILE_TEMPLATE.strip()
        p2v = {
            "[domain]": self.domain,
            "[email]": self.email,
            "[username]": self.username,
            "[password]": self.password,
        }
        for placeholder in p2v:
            caddyfile = caddyfile.replace(placeholder, p2v[placeholder])
        return caddyfile

    def get_v2rayn_custom_server(self):
        v2rayn_custom_server = V2RAYN_TEMPLATE.strip()
        proxy = f"{self.scheme}://{self.username}:{self.password}@{self.domain}"
        return v2rayn_custom_server.replace("[proxy]", proxy)

    def get_nekoray_sharelink(self):
        typecode = f"{self.username}:{self.password}@{self.domain}:{self.port}#{self.domain}"
        sharelink = f"naive+{self.scheme}://{typecode}"
        return sharelink

    def get_shadowrocket_sharelink(self):
        typecode = f"{self.username}:{self.password}@{self.domain}:{self.port}"
        sharelink = f'http2://{base64.b64encode(typecode.encode("utf8")).decode("utf8")}'
        return sharelink.replace("=", "")


def check_caddy(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not os.path.isfile(PATH_CADDY) or not os.path.getsize(PATH_CADDY):
            logging.error(f"Naiveproxy 未初始化，請先執行「敏捷部署」 - func={func.__name__}")
        else:
            return func(*args, **kwargs)

    return wrapped


def skip_recompile(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if os.path.isfile(PATH_CADDY) and os.path.getsize(PATH_CADDY):
            logging.error(f"Naiveproxy 已编译，如需修改参数请执行「重新配置」 - func={func.__name__}")
        else:
            return func(*args, **kwargs)

    return wrapped


class ClientSettingsManager:
    dir_workspace = WORKSPACE
    path_caddyfile = os.path.join(dir_workspace, "Caddyfile")
    path_v2rayn_socks5 = os.path.join(dir_workspace, "v2rayn_socks5_config.txt")
    path_sharelink_nekoray = os.path.join(dir_workspace, "nekoray_sharelink.txt")
    path_config_server = os.path.join(dir_workspace, "caddy_server.json")
    path_client_config = os.path.join(dir_workspace, "clients.json")

    def __init__(self):
        self.caddy = self._preload_config()

    def _preload_config(self) -> CaddyServer:
        os.makedirs(self.dir_workspace, exist_ok=True)
        try:
            with open(self.path_config_server, "r", encoding="utf8") as file:
                return CaddyServer(**json.load(file))
        except (FileNotFoundError, KeyError, TypeError):
            return CaddyServer()

    def refresh_localcache(self, drop: bool = False):
        """修改 Caddyfile 以及客户端配置"""
        localcache = {
            "v2rayn_custom_server": self.caddy.get_v2rayn_custom_server(),
            "nekoray_sharelink": self.caddy.get_nekoray_sharelink(),
            "shadowrocket_sharelink": self.caddy.get_shadowrocket_sharelink(),
        }
        with open(self.path_client_config, "w", encoding="utf8") as file:
            json.dump(localcache, file)
        with open(self.path_config_server, "w", encoding="utf8") as file:
            json.dump(self.caddy.__dict__, file, indent=4)
        with open(self.path_caddyfile, "w", encoding="utf8") as file:
            file.write(self.caddy.get_caddyfile())

        if drop:
            print(" ↓ ↓ V2RayN ↓ ↓ ".center(50, "="))
            print(localcache.get("v2rayn_custom_server"))
            print(" ↓ ↓ NekoRay & Matsuri ↓ ↓ ".center(50, "="))
            print(f"\n{localcache.get('nekoray_sharelink')}\n")
            print(" ↓ ↓ Shadowrocket ↓ ↓ ".center(50, "="))
            print(f"\n{localcache.get('shadowrocket_sharelink')}\n")


class CaddyServiceControl:
    def __init__(self, path_caddy):
        self.path_caddy = path_caddy

    @check_caddy
    def caddy_start(self):
        """后台运行 CaddyServer"""
        os.system(f"cd {os.path.dirname(self.path_caddy)} && ./caddy start >/dev/null 2>&1")
        logging.info("Start the naiveproxy")

    @check_caddy
    def caddy_stop(self):
        """停止 CaddyServer"""
        os.system(f"cd {os.path.dirname(self.path_caddy)} && ./caddy stop >/dev/null 2>&1")
        logging.info("Stop the naiveproxy")

    @check_caddy
    def caddy_reload(self):
        """重启 CaddyServer 重新读入配置"""
        os.system(f"cd {os.path.dirname(self.path_caddy)} && ./caddy reload >/dev/null 2>&1")
        logging.info("Reload the naiveproxy")

    @check_caddy
    def caddy_status(self):
        """查看 CaddyServer 运行状态"""


class NaiveproxyPanel:

    def __init__(self):
        self.path_caddy = PATH_CADDY
        self.csm = ClientSettingsManager()
        self.caddy = self.csm.caddy
        self.utils = CaddyServiceControl(self.path_caddy)

    def _compile(self):
        # ==================== preprocess ====================
        os.system("clear")
        logging.info("Check snap, wget, port80 and port443")
        cmd_queue = ("apt install -y snapd wget >/dev/null 2>&1", "nginx -s stop >/dev/null 2>&1")
        for cmd in cmd_queue:
            os.system(cmd)
        # ==================== handle server ====================
        logging.info("Check go1.18+")
        os.system("apt remove golang-go -y >/dev/null 2>&1")
        os.system("snap install go --classic >/dev/null 2>&1")

        logging.info("Check xcaddy")
        cmd_queue = (
            "wget https://github.com/caddyserver/xcaddy/releases/download/v0.3.1/xcaddy_0.3.1_linux_amd64.deb >/dev/null 2>&1",
            "apt install -y ./xcaddy_0.3.1_linux_amd64.deb >/dev/null 2>&1",
            "rm xcaddy_0.3.1_linux_amd64.deb",
        )
        for cmd in cmd_queue:
            os.system(cmd)

        os.makedirs(os.path.dirname(self.path_caddy), exist_ok=True)
        if not os.path.isfile(self.path_caddy):
            logging.info("Build caddy with naiveproxy")
            os.system(
                f"xcaddy build "
                f"--output {self.path_caddy} "
                f"--with github.com/caddyserver/forwardproxy@caddy2=github.com/klzgrad/forwardproxy@naive"
            )
        else:
            logging.info("Caddy already exists, skip compilation")
            logging.info(self.path_caddy)

        # ==================== Network FineTune ====================
        logging.info("Naiveproxy Network Performance Tuning")
        cmd_queue = (
            "sudo sysctl -w net.ipv4.tcp_congestion_control=bbr >/dev/null 2>&1",
            "sudo sysctl -w net.ipv4.tcp_slow_start_after_idle=0 >/dev/null 2>&1",
            "sudo sysctl -w net.ipv4.tcp_notsent_lowat=16384 >/dev/null 2>&1",
        )
        for cmd in cmd_queue:
            os.system(cmd)

    @staticmethod
    def _guide_domain(prompt: str):
        pattern = re.compile(r"(?:\w(?:[\w\-]{0,61}\w)?\.)+[a-zA-Z]{2,6}")
        while True:
            domain = input(prompt).strip()
            result = re.findall(pattern, domain)
            if result and result.__len__() == 1:
                return result[0]

    @skip_recompile
    def deploy_naiveproxy(self):
        self.caddy.username = input(">> 输入用户名[username](回车随机配置)：").strip() or self.caddy.username
        self.caddy.password = input(">> 输入密码[password](回车随机配置)：").strip() or self.caddy.password
        self.caddy.domain = self._guide_domain(prompt=">> 输入解析到本机Ipv4的域名[domain]：")
        self._compile()
        if not os.path.isfile(self.path_caddy):
            logging.error("編譯失敗")
        else:
            logging.info("按任意键部署 Naiveproxy 系统服务")
            input()
            self.csm.refresh_localcache(drop=True)  # deploy
            self.utils.caddy_start()

    @check_caddy
    def delete(self):
        """删除 np-start 缓存"""
        if input(">> 卸载「已编译的Caddy服務及缓存數據」[y/n]").strip().lower().startswith("y"):
            self.utils.caddy_stop()
            os.system(f"rm -rf {WORKSPACE} >/dev/null 2>&1")
            logging.info("Delete cache of the naiveproxy")
        else:
            logging.info(f"Withdraw operation")

    @check_caddy
    def check_config(self):
        """查看客户端配置信息"""
        self.csm.refresh_localcache(drop=True)  # check

    @check_caddy
    def reset_user_config(self):
        if input(">> 是否使用上次配置的用戶名？[y/n]").strip().lower().startswith("n"):
            self.caddy.username = input(">> 输入用户名[username](回车随机配置)：").strip()
        if input(">> 是否使用上次配置的密碼？[y/n]").strip().lower().startswith("n"):
            self.caddy.password = input(">> 输入密码[password](回车随机配置)：").strip()
        if input(f">> 是否使用上次配置的域名({self.caddy.domain})？[y/n]").strip().lower().startswith("n"):
            self.caddy.domain = self._guide_domain(prompt=">> 输入解析到本机Ipv4的域名[domain]：")

        self.csm.refresh_localcache()  # reset
        logging.info("reset user config")
        self.utils.caddy_reload()

    def guide_menu(self):
        if not (item := input(GUIDER_PANEL).strip()):
            return

        if item == "1":
            self.deploy_naiveproxy()
        elif item == "2":
            self.delete()
        elif item == "3":
            self.utils.caddy_start()
        elif item == "4":
            self.utils.caddy_stop()
        elif item == "5":
            self.utils.caddy_reload()
        elif item == "6":
            self.utils.caddy_status()
        elif item == "7":
            self.check_config()
        elif item == "8":
            self.reset_user_config()


if __name__ == "__main__":
    try:
        NaiveproxyPanel().guide_menu()
    except KeyboardInterrupt:
        print("\n")
