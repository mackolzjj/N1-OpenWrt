<div align="center">

# Phicomm N1 · OpenWrt

> 本仓库由 `Phicomm-N1_OpenWrt` 复制而来，唯一区别是内核改用自编译的 [`mackolzjj/ophub-kernel-ftrace`](https://github.com/mackolzjj/ophub-kernel-ftrace)：开启 `CONFIG_FUNCTION_TRACER` / `CONFIG_DYNAMIC_FTRACE`，供 honk 的 fentry UDP 接收追踪使用；固件内 `/etc/config/amlogic` 的在线更新源也已同步指向本库与该内核仓库。

**官方 OpenWrt 精简编译的斐讯 N1 旁路由固件** · eBPF / BTF 就绪 · 纯有线

[![Build](https://github.com/mackolzjj/N1-OpenWrt/actions/workflows/armsr_armv8.yml/badge.svg)](https://github.com/mackolzjj/N1-OpenWrt/actions/workflows/armsr_armv8.yml)
[![Release](https://img.shields.io/github/v/release/mackolzjj/N1-OpenWrt?label=Release)](https://github.com/mackolzjj/N1-OpenWrt/releases)
![Source](https://img.shields.io/badge/OpenWrt-v25.12.6-orange)
![Kernel](https://img.shields.io/badge/kernel-6.12.y-blue)
![Board](https://img.shields.io/badge/board-s905d%20%2F%20aarch64-green)
![Package](https://img.shields.io/badge/pkg-apk-lightgrey)

</div>

> 旁路由定位：拨号与 WiFi 交给主路由，本固件**不含 PPPoE / WiFi**；**不内置 honk / doona**，只把内核的 eBPF / BTF 底座准备好。

## ✨ 特性

- **纯净底座**：官方 OpenWrt `v25.12.6` + `apk`，无代理组件、无第三方主题，把选择权留给设备端
- **eBPF 全链路就绪**：`BPF_EVENTS` / `DEBUG_INFO_BTF` / `XDP_SOCKETS` = y，`vmlinux-btf-builtin`，刷机即可自行安装 honk / dae 类程序
- **容器与界面**：`podman` + LuCI、`luci-app-amlogic`（晶晨宝盒）
- **日常工具**：`bsdtar` / `btrfs-progs` / `f2fs-tools` / `xfs-*` / `pigz` / `tar` / `gawk` / `perl-*` / `chattr` / `lsattr` / `fstrim` / `zoneinfo-asia`
- **预置调优**：每日 04:00 `fstrim -a`，CPU `performance` 锁 1.512 GHz，晶晨宝盒在线更新已指向本库

## 🚀 快速开始

从 [Releases](https://github.com/mackolzjj/N1-OpenWrt/releases) 取 `openwrt_amlogic_s905d_k6.12.*.img.gz` 并解压，写入 U 盘启动：

```bash
openwrt-install-amlogic      # 需要固化到 eMMC 时执行
# 浏览器打开 http://192.168.2.2    root / password
```

开机后建议核对：

```bash
grep PRETTY_NAME /etc/os-release; uname -r
ls -l /sys/kernel/btf/vmlinux      # 装 honk / dae 前必须存在
uci show amlogic.config | grep -E 'firmware|kernel_branch'
```

预期 `OpenWrt 25.12.6`、`6.12.x-ophub`、BTF 文件存在。

> ⚠️ 建议**全新刷写、不保留配置**。本线不含 honk / doona，需要透明代理请在设备端按架构自行安装，或直接刷另一条 [`Phicomm-N1_ImmortalWrt`](https://github.com/mackolzjj/Phicomm-N1_ImmortalWrt)（编译内置）。

## ⚙️ 构建与发布

| | |
| --- | --- |
| 源码 | `openwrt/openwrt` @ `v25.12.6` → `armsr/armv8` |
| 内核 | **自编译** [`mackolzjj/ophub-kernel-ftrace`](https://github.com/mackolzjj/ophub-kernel-ftrace) · `kernel_stable` `6.12.y` + `auto_kernel: true` |
| 打包 | `ophub/amlogic-s9xxx-openwrt` · `s905d` · `256/1024` · builder `Mackol` |
| 触发 | push `main` / `master`、手动、每月 1 / 16 日 08:00（北京时间） |
| Release | `OpenWrt_<分支>_<YYYYMMDD>`（当前 `OpenWrt_main_日期`），同日 `--clobber` 覆盖，仅留最近 10 个 |

<details>
<summary><b>展开：完整构建参数 · 在线更新 · 排错 · 自定义编译</b></summary>

### 构建参数

| 参数 | 值 |
| --- | --- |
| 构建机 | `ubuntu-24.04`，`TZ=Asia/Shanghai`；77 个 apt 编译依赖已固化在 workflow 内，不再外部拉取 |
| `diy.sh` | clone `daeuniverse/openwrt-packages`（仅取 `vmlinux-btf-builtin`）、`ophub/luci-app-amlogic`、`Zerogiven-OpenWRT-Packages/luci-app-podman`；移除 `luci-app-attendedsysupgrade` |
| 内核选项 | `CONFIG_KERNEL_BPF_EVENTS` / `CONFIG_KERNEL_DEBUG_INFO_BTF` / `CONFIG_KERNEL_XDP_SOCKETS` = y；官方 OpenWrt 无 `CONFIG_BPF_TOOLCHAIN_HOST` 符号，未启用 |
| 遗留步骤 | workflow 仍安装 `bpf-linker` v0.13.0（原为 honk 编译准备），本线不编译 honk，属无害保留 |
| 默认网络 | `eth0` 静态 `192.168.2.2/24`，网关 `192.168.2.1`，仅 `lan` 无 wan |
| 不集成 | `ppp` / `kmod-ppp` / `kmod-mppe`（无 PPPoE）、无线组件（`ENABLE_WIFI_K510=0`）、`luci-app-samba4`、`luci-app-filetransfer`、honk / doona |
| 产物名 | `openwrt_amlogic_s905d_k6.12.*_<日期>.img.gz`（ophub 生成，与 Release 名不同） |

### 晶晨宝盒在线更新

`/etc/config/amlogic` 已预置四项指向本库：`firmware_repo = mackolzjj/N1-OpenWrt`、`firmware_tag = OpenWrt`、`firmware_suffix = .img.gz`、`kernel_branch = 6.12`（与 `6.12.y` 对齐）。

> 这套配置与本库 Release 名天然匹配（`OpenWrt_main_日期` 含 `OpenWrt` 关键字），只要仓库有 Release，列表就有内容；上限 10 个。`amlogic_kernel_path` / `amlogic_kernel_tags` 属于内核在线更新，仍指向 `ophub/kernel`。

### 常见问题

| 现象 | 排查 |
| --- | --- |
| 在线更新列表为空 | 先确认仓库已发布 Release；再核对上述四项配置；列表上限 10 个 |
| `/sys/kernel/btf/vmlinux` 不存在 | 运行时内核由 ophub 打包时替换，BTF 取决于 `kernel_stable`；自行换过内核或刷错镜像会丢失，honk / dae 会直接退出 |
| LuCI 无 honk / doona 菜单 | 设计如此，本线不内置；需设备端自装，或改刷 `Phicomm-N1_ImmortalWrt` |
| 无法拨号 / 无 WiFi | 设计如此，`.config` 明确禁用 ppp 与无线组件 |

### 自定义编译

`armsr/armv8/N1/.config`（内置包 / 内核选项）· `armsr/armv8/diy/diy.sh`（软件源）· `armsr/armv8/N1/files/`（预置 `/etc/config` 与 crontabs）· `armsr/armv8/N1/mk_s905d_n1.sh`（本地打包）· `.github/workflows/armsr_armv8.yml`（触发、内核、Release 规则）。

改动后推送到 `main` / `master` 会触发构建；仅改文档且不想编译时，在 commit body 写 `[skip ci]`。

</details>

## 🙏 致谢

[OpenWrt](https://github.com/openwrt/openwrt) · [ophub/amlogic-s9xxx-openwrt](https://github.com/ophub/amlogic-s9xxx-openwrt) · [ophub/kernel](https://github.com/ophub/kernel) · [daeuniverse/openwrt-packages](https://github.com/daeuniverse/openwrt-packages) · [luci-app-podman](https://github.com/Zerogiven-OpenWRT-Packages/luci-app-podman)
