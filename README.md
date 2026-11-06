<div align="center">

# Phicomm N1 · OpenWrt 25.12

**官方 OpenWrt 源码 + 自编译内核**，面向斐讯 N1（s905d）的有线旁路由固件。

[![Build](https://github.com/mackolzjj/N1-OpenWrt/actions/workflows/armsr_armv8.yml/badge.svg)](https://github.com/mackolzjj/N1-OpenWrt/actions/workflows/armsr_armv8.yml)
[![Release](https://img.shields.io/github/v/release/mackolzjj/N1-OpenWrt?label=Release)](https://github.com/mackolzjj/N1-OpenWrt/releases)
![OpenWrt](https://img.shields.io/badge/OpenWrt-v25.12.6-orange)
![Kernel](https://img.shields.io/badge/kernel-6.12.y-blue)

</div>

> 不含 PPPoE / WiFi，也**不内置 honk / dae / doona** —— 只准备 eBPF / BTF / ftrace / NFQUEUE 内核底座，透明代理自行安装。

## 固件内容

| | |
| --- | --- |
| 源码 / 架构 | OpenWrt `v25.12.6`，`armsr/armv8`，`apk` |
| 运行内核 | [`mackolzjj/ophub-kernel-ftrace`](https://github.com/mackolzjj/ophub-kernel-ftrace) 的 `kernel_stable` / `6.12.y`，打包阶段整体替换；开启 `FUNCTION_TRACER`、`DYNAMIC_FTRACE`、`DEBUG_INFO_BTF`、`BPF_JIT`、`NFT_QUEUE`。`.config` 里的 `CONFIG_KERNEL_*` 只作用于 OpenWrt 自身产物 |
| 登录 / Web | `root` / **空密码**，`http://192.168.2.2`，LuCI + uhttpd |
| 网络 | `eth0` 静态 `192.168.2.2/24`，网关 `192.168.2.1`；**无 DNS、无 wan**；已关 `send_redirects` / `rp_filter`（单臂旁路由） |
| 界面 | 简体中文 `zh_cn`（可切英文）、Argon 主题、6 个 `luci-i18n-*-zh-cn` 包 |
| 内置应用 | `luci-app-amlogic`（晶晨宝盒）、`luci-app-podman` + `podman`、常用磁盘/压缩工具、`zoneinfo-asia` |
| 时区 / 定时 | `CST-8` / `Asia/Shanghai`，每日 04:00（北京时间）`fstrim -a` |
| 在线更新源 | 固件 `mackolzjj/N1-OpenWrt`、内核 `mackolzjj/ophub-kernel-ftrace`，由首次启动脚本写回 |
| 禁用 | `ppp`、无线驱动、`luci-app-samba4`、`luci-app-filetransfer`、honk / doona |

## 注意

- Release 说明中的 `密码: password` 是 workflow 模板文字，实际为空密码。
- 静态 `files/etc/config/amlogic` 已删除（会被 ophub 覆盖，且 `write_bootloader='1'` 有风险）；U 盘启动与安装 eMMC 不受影响。
- 第三方 feed 用 `--depth=1` 拉默认分支、未锁版本；`bpf-linker` 是保留的冗余单点依赖。

## 致谢

[OpenWrt](https://github.com/openwrt/openwrt) · [ophub/amlogic-s9xxx-openwrt](https://github.com/ophub/amlogic-s9xxx-openwrt) · [ophub/kernel](https://github.com/ophub/kernel) · [daeuniverse/openwrt-packages](https://github.com/daeuniverse/openwrt-packages) · [luci-app-amlogic](https://github.com/ophub/luci-app-amlogic) · [luci-theme-argon](https://github.com/jerrykuku/luci-theme-argon) · [luci-app-podman](https://github.com/Zerogiven-OpenWRT-Packages/luci-app-podman)
