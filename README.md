# npstart

Ubuntu20.04+ 一键编译 Naiveproxy

## Quick Start

```shell
wget -qO /home/npstart.py https://raw.githubusercontent.com/QIN2DIM/np-start/main/main.py && python3 /home/npstart.py
```

之后可通过快捷指令 `npstart` 运行脚本。

## Features

- [x] 自动编译最新版 Naiveproxy，注册系统服务，脚手架模式管理系统服务
- [x] 自动配置 BBR+FQ 拥塞控制策略
- [x] 优化 HTTP/2 网络环境，大幅度提升吞吐量，降低延时
- [ ] 监听、拉取、更新代理核心

## Reference

[Run Caddy as a daemon · klzgrad/naiveproxy Wiki](https://github.com/klzgrad/naiveproxy/wiki/Run-Caddy-as-a-daemon)

[caddyserver/xcaddy: Build Caddy with plugins](https://github.com/caddyserver/xcaddy)

[Caddyfile Concepts — Caddy Documentation](https://caddyserver.com/docs/caddyfile/concepts#structure)

[Optimizing HTTP/2 prioritization with BBR and tcp_notsent_lowat](https://blog.cloudflare.com/http-2-prioritization-with-nginx/)

[Optimizing TCP for high WAN throughput while preserving low latency | Noise](https://noise.getoto.net/2022/07/01/optimizing-tcp-for-high-wan-throughput-while-preserving-low-latency/)

