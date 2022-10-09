# -*- coding: utf-8 -*-
# Time       : 2022/10/9 13:06
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import logging
import os
import random
import sys
import uuid
from dataclasses import dataclass

# 阻止 python2 及非 linux 系统运行
if sys.version_info[0] < 3 or sys.platform != "linux":
    sys.exit()

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
    "listen": "socks://127.0.0.1:[listen_port]",
    "proxy": "https://[username]:[password]@[domain]"
}
"""

NEKORAY_TEMPLATE = """
-- 通用 -- 
名称: NaiveTurtle
地址: [domain]
端口: [port]
-- Naive --
用户名: [username]
密码: [password]
协议: https
SNI: [domain]
不安全并发: 0
"""


@dataclass
class Config:
    dir_workspace = "/home/naiveproxy"
    dir_conf = os.path.join(dir_workspace, "conf")
    path_caddyfile = os.path.join(dir_workspace, "Caddyfile")
    path_caddy = os.path.join(dir_workspace, "caddy")
    username = ""
    password = ""
    email = ""
    domain = ""
    sni = ""
    port = "443"
    scheme = "https"  # "https" or "quic"

    def __post_init__(self):
        os.makedirs(self.dir_workspace, exist_ok=True)
        os.makedirs(self.dir_conf, exist_ok=True)


config = Config()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
)


def preprocess():
    os.system("clear")

    logging.info("Check snap, wget, port80 and port443")
    cmd_queue = ("apt install -y snapd wget >/dev/null 2>&1", "nginx -s stop >/dev/null 2>&1")
    for cmd in cmd_queue:
        os.system(cmd)


def handle_server():
    logging.info("Check go1.18+")
    os.system("apt remove golang-go -y >/dev/null 2>&1")
    os.system("snap install go --classic >/dev/null 2>&1")

    logging.info("Check xcaddy ")
    cmd_queue = (
        "wget https://github.com/caddyserver/xcaddy/releases/download/v0.3.1/xcaddy_0.3.1_linux_amd64.deb >/dev/null 2>&1",
        "apt install -y ./xcaddy_0.3.1_linux_amd64.deb >/dev/null 2>&1",
        "rm xcaddy_0.3.1_linux_amd64.deb",
    )
    for cmd in cmd_queue:
        os.system(cmd)

    if not os.path.isfile(config.path_caddy):
        logging.info("Build caddy with naiveproxy")
        os.system(
            f"xcaddy build "
            f"--output {config.path_caddy} "
            f"--with github.com/caddyserver/forwardproxy@caddy2=github.com/klzgrad/forwardproxy@naive"
        )
    else:
        logging.info("Caddy already exists, skip compilation")


def guider_input():
    """引导输入，生成配置模版"""

    def output(template):
        with open(config.path_caddyfile, "w", encoding="utf8") as file:
            file.write(template)

    while not (domain := input("请输入域名 ---> ").strip()):
        pass

    tmp = CADDYFILE_TEMPLATE
    config.domain = domain
    config.username = f"{uuid.uuid4().hex}"[:8]
    config.password = uuid.uuid4().hex
    config.email = f"{str(uuid.uuid4().hex)[:8]}@tesla.com"
    placeholder2val = {
        "[domain]": domain,
        "[email]": config.email,
        "[username]": config.username,
        "[password]": config.password,
    }
    for placeholder in placeholder2val:
        tmp = tmp.replace(placeholder, placeholder2val[placeholder])

    print(f" Caddyfile ".center(50, "="), tmp)

    output(tmp)


def dropout_client_config_v2rayn():
    tmp = V2RAYN_TEMPLATE
    p2v = {
        "[domain]": config.domain,
        "[username]": config.username,
        "[password]": config.password,
        "[listen_port]": f"{random.randint(50000, 60000)}",
    }
    for p in p2v:
        tmp = tmp.replace(p, p2v[p])

    print(" V2RayN ".center(50, "="), tmp)
    path_output = os.path.join(config.dir_conf, "v2rayn_naive.json")
    with open(path_output, "w", encoding="utf8") as file:
        file.write(tmp)


def dropout_client_config_nekoray():
    tmp = NEKORAY_TEMPLATE
    p2v = {
        "[domain]": config.domain,
        "[username]": config.username,
        "[password]": config.password,
        "[port]": config.port,
    }
    for p in p2v:
        tmp = tmp.replace(p, p2v[p])

    share_link = (
        f"naive+{config.scheme}://{config.username}:{config.password}@{config.domain}#NaiveNode"
    )
    print(" NekoRay/Matsuri ".center(50, "="), tmp)
    print(" NekoRay/Matsuri 分享链接", share_link)
    path_output = os.path.join(config.dir_conf, "nekoray_naive.txt")
    with open(path_output, "w", encoding="utf8") as file:
        file.write(tmp)


def autorun():
    logging.info("按任意键部署 Naiveproxy 后台任务")
    input("")
    os.system(f"cd {config.dir_workspace} && ./caddy start")


if __name__ == "__main__":
    preprocess()
    handle_server()
    if os.path.isfile(config.path_caddy):
        guider_input()
        autorun()
        dropout_client_config_v2rayn()
        dropout_client_config_nekoray()
    else:
        logging.error("编译失败")
