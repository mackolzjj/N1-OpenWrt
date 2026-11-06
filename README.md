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

## 刷机

1. [Releases](https://github.com/mackolzjj/N1-OpenWrt/releases) 取 `openwrt_amlogic_s905d_k6.12.*.img.gz` 写 U 盘；列表为空则先去 Actions **Run workflow**。
2. 浏览器打开 `http://192.168.2.2`，用户 `root`，密码留空。需要固化到 eMMC 执行 `openwrt-install-amlogic`（不改写 bootloader）。
3. **全新刷写、不保留配置** —— 三个 `zz-*` 首次启动脚本只在首次启动执行一次。

确认内核没被换回官方版本：

```sh
ls -l /sys/kernel/btf/vmlinux
cat /sys/kernel/debug/tracing/available_tracers        # 应含 function / function_graph
grep -E 'CONFIG_(FUNCTION_TRACER|DYNAMIC_FTRACE)=y' /boot/config-*
```

首次启动后手动处理（仓库未固化）：

```sh
uci add_list network.lan.dns='223.5.5.5'; uci commit network    # 补 DNS，否则 apk update 等可能解析失败
uci set dhcp.lan.ignore='1'                                      # 关 LAN DHCP，避免和主路由抢地址
uci set dhcp.lan.dhcpv6='disabled'; uci set dhcp.lan.ra='disabled'; uci commit dhcp
passwd                                                            # 设置 root 密码
reboot                                                            # network restart 会掐断 SSH
```

## 构建

`openwrt/openwrt@v25.12.6` → 编译 `armsr/armv8` 的 `rootfs.tar.gz`（`.config` + `files/` + `diy.sh`）→ `ophub/amlogic-s9xxx-openwrt@main`（`s905d`、`256/1024`、注入自编译内核）→ `.img.gz` → Release。

- 触发：Actions 手动 `Run workflow`；push `main` / `master`；每月 1、16 日 UTC 00:00（北京 08:00）。提交信息含 `[skip ci]` 可跳过 push 构建。
- Release：`OpenWrt_<分支>_<YYYYMMDD>`，同日覆盖，保留最近 10 个；晶晨宝盒 `firmware_tag=OpenWrt` 与之匹配。
- **构建后必查**：`Download package` 日志里 `== 已启用的简体中文翻译包 ==` 必须列出 **6 行** `CONFIG_PACKAGE_luci-i18n-*-zh-cn=y`；只有 `::warning::` 就别刷机（该检查不会让构建失败）。
- LAN IP 由 `files/etc/config/network` 决定，ophub 的 `openwrt_ip` 在本线不生效。

## 文件地图

| 路径 | 作用 |
| --- | --- |
| `.github/workflows/armsr_armv8.yml` | 唯一构建流水线（13 步） |
| `armsr/armv8/N1/.config` | 目标、软件包、中文包开关、`rootfs.tar.gz` |
| `armsr/armv8/N1/files/etc/config/`、`sysctl.d/`、`crontabs/` | 语言主题、IP、旁路由内核参数、fstrim |
| `armsr/armv8/N1/files/etc/uci-defaults/zz-*` | 首次启动锁定 Argon、写回在线更新源、设时区 |
| `armsr/armv8/diy/diy.sh`、`diy/po/` | 4 个第三方 feed、简体中文补译（由 `luci.mk` 编进 apk，仓库无二进制 `.lmo`） |
| `armsr/armv8/N1/mk_s905d_n1.sh` | 上游模板的本地打包脚本，缺依赖且 **Actions 不使用** |

改配置后需重新构建才进固件；只改文档用 `[skip ci]`。

## 注意

- Release 说明中的 `密码: password` 是 workflow 模板文字，实际为空密码。
- 静态 `files/etc/config/amlogic` 已删除（会被 ophub 覆盖，且 `write_bootloader='1'` 有风险）；U 盘启动与安装 eMMC 不受影响。
- 第三方 feed 用 `--depth=1` 拉默认分支、未锁版本；`bpf-linker` 是保留的冗余单点依赖。

## 致谢

[OpenWrt](https://github.com/openwrt/openwrt) · [ophub/amlogic-s9xxx-openwrt](https://github.com/ophub/amlogic-s9xxx-openwrt) · [ophub/kernel](https://github.com/ophub/kernel) · [daeuniverse/openwrt-packages](https://github.com/daeuniverse/openwrt-packages) · [luci-app-amlogic](https://github.com/ophub/luci-app-amlogic) · [luci-theme-argon](https://github.com/jerrykuku/luci-theme-argon) · [luci-app-podman](https://github.com/Zerogiven-OpenWRT-Packages/luci-app-podman)
