# np-start

Ubuntu20.04+ 自动编译 Naiveproxy

## Quick Start

```shell
wget -O npstart.py https://raw.githubusercontent.com/QIN2DIM/np-start/main/main.py && python3 npstart.py
```

## 脚本执行流

### 预准备

1. 检查 apt packages: snap

   ```shell
   apt install -y snapd
   ```

2. 确保 80,443 端口无占用

   通常认为是 nginx 占用

   ```shell
   nginx -s stop
   ```

   或通过以下指令检查端口占用

   ```shell
   lsof -i:80
   lsof -i:443
   ```

### 自动编译

1. 安装 golang 1.18.5

   这一步执行前会先通过 `apt remove -y golang-go` 卸载低版本语言包。

   ```shell
   snap install go --classic
   ```

2. 安装 xcaddy

   ```shell
   wget https://github.com/caddyserver/xcaddy/releases/download/v0.3.1/xcaddy_0.3.1_linux_amd64.deb && apt install -y ./xcaddy_0.3.1_linux_amd64.deb && rm xcaddy_0.3.1_linux_amd64.deb
   ```


3. 编译 Naiveproxy

   根据硬件配置需要 1 ~ 5分钟。

   编译结束后，在 output 目录下生成一个名为 `caddy` 的二进制文件，通过它运行携带 Naiveproxy 的 Caddy2 服务器。

   ```shell
   xcaddy build --output /home/caddy --with github.com/caddyserver/forwardproxy@caddy2=github.com/klzgrad/forwardproxy@naive
   ```

### 编写配置文件

编写 Caddyfile，在 output 目录下创建一个名为 Caddyfile 的文本文件，这里写入 Naiveproxy 的基础配置。

配置文件中的 `[占位符]` 需要手动替换，当然默认的运行端口（443）也可以更改，但不推荐，除非情况特殊。此时你需要使用 `config` 模版文件，请访问 Caddy 官方文档获取更多信息。

```wiki
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
```

### 启动 Naiveproxy

`/home/caddy` 为 output 输出路径，根据你自己的参数而定。通过 `caddy --help` 查看所有指令。

1. 前台运行

   ```shell
   cd /home && ./caddy run
   ```

2. 后台运行

   ```shell
   cd /home && ./caddy start
   ```

3. 开机自启

##  客户端配置

使用图形化界面运行 Naiveproxy Core：

- Windows: NekoRay，V2RayN

- Android: Matsuri

- iOS: shadowrocket

