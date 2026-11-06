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

- **纯净底座**：官方 OpenWrt `v25.12.6` + `apk`，不内置代理组件，预置 Argon 主题与简体中文界面
- **eBPF 全链路就绪**：自编译内核开启 `DEBUG_INFO_BTF` / `BPF_JIT` / `FUNCTION_TRACER` / `DYNAMIC_FTRACE`，提供 `/sys/kernel/btf/vmlinux` 与 BPF trampoline，刷机即可自行安装 honk / dae 类程序
- **内核在打包阶段整体替换**：`armsr/armv8/N1/.config` 里的 `CONFIG_KERNEL_*` 只作用于 OpenWrt 自身编译产物；最终运行内核由 `ophub/amlogic-s9xxx-openwrt` 注入，其选项取决于内核仓库的 `config-6.12`
- **容器与界面**：`podman` + LuCI、`luci-app-amlogic`（晶晨宝盒）
- **中文开箱可用**：默认 `lang=zh_cn`；`diy.sh` 把补译 `.po` 注入三个第三方 feed 包的 `po/zh_Hans/`，`CONFIG_LUCI_LANG_zh_Hans=y` 让 `luci.mk` 把每个 `.po` 编成同名 `.lmo` 并打进 `luci-i18n-*-zh-cn` apk 包（进 apk 数据库、`apk upgrade` 可升级）。仓库不含任何二进制 `.lmo`，也没有构建期手工复制步骤
- **默认主题 Argon**：`files/etc/uci-defaults/zz-luci-argon-theme` 在首次启动最后执行，把 `mediaurlbase` 与 4 个 themes 值统一写成 `/luci-static/...` 绝对路径并锁定为 Argon，避免主题包的 uci-defaults 覆盖成 Bootstrap 或写入短名导致 CSS 404；之后仍可在「系统 → 系统 → 语言与界面」切换主题
- **日常工具**：`bsdtar` / `btrfs-progs` / `f2fs-tools` / `xfs-*` / `pigz` / `tar` / `gawk` / `perl-*` / `chattr` / `lsattr` / `fstrim` / `zoneinfo-asia`
- **在线更新源锁定**：`files/etc/uci-defaults/zz-amlogic-repo` 在首次启动最后把晶晨宝盒的固件 / 内核下载仓库写回 `mackolzjj/N1-OpenWrt` 与 `mackolzjj/ophub-kernel-ftrace`，避免被打包阶段的 ophub 默认值覆盖后误更新为官方内核（会丢失 ftrace / NFQUEUE / BTF）
- **预置调优**：每日 04:00 `fstrim -a`。注意 `files/etc/config/amlogic` 里的 `ext4` 与 CPU `performance` 锁频模板项会被 ophub 打包默认值覆盖，当前未生效

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
cat /sys/kernel/debug/tracing/available_tracers                    # 应含 function / function_graph
grep -E 'CONFIG_(FUNCTION_TRACER|DYNAMIC_FTRACE)=y' /boot/config-*   # 两行都应有输出
uci show amlogic.config | grep -E 'firmware|kernel_branch'
```

预期 `OpenWrt 25.12.6`、`6.12.x-ophub`、BTF 文件存在；`available_tracers` 不再只有 `nop`（官方内核只有 `nop`），且两个 ftrace 配置项都有输出。**这两条是本仓库区别于默认固件的关键**，缺失说明打包时拉回了官方内核。

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
| `diy.sh` | clone `daeuniverse/openwrt-packages`（仅取 `vmlinux-btf-builtin`）、`ophub/luci-app-amlogic`、`Zerogiven-OpenWRT-Packages/luci-app-podman`；移除 `luci-app-attendedsysupgrade`；补齐三个插件的 `po/zh_Hans` 并注入 `diy/po/*-extra.po` 补译 |
| 中文语言包 | 唯一路径：`luci.mk` 扫描各包 `po/zh_Hans/*.po`，每个 `.po` 由构建系统自带 `po2lmo` 编成同名 `.lmo`，全部打进 `luci-i18n-{base,firewall,package-manager,amlogic,podman,argon-config}-zh-cn` 六个 apk 包；`diy.sh` 注入的 `*-extra.po` 因此自动成为 `*-extra.zh-cn.lmo`。无兜底、无仓库内二进制 |
| 内核选项 | `armsr/armv8/N1/.config` 的 `CONFIG_KERNEL_BPF_EVENTS` / `CONFIG_KERNEL_DEBUG_INFO_BTF` / `CONFIG_KERNEL_XDP_SOCKETS` = y，仅作用于 OpenWrt 自身编译产物；最终运行内核在打包阶段被整体替换，选项取自内核仓库 `config-6.12`（`DEBUG_INFO_BTF` / `FUNCTION_TRACER` / `DYNAMIC_FTRACE` = y）。官方 OpenWrt 无 `CONFIG_BPF_TOOLCHAIN_HOST` 符号，未启用 |
| 遗留步骤 | workflow 仍安装 `bpf-linker` v0.13.0（原为 honk 编译准备），本线不编译 honk，属无害保留 |
| 默认网络 | `eth0` 静态 `192.168.2.2/24`，网关 `192.168.2.1`，仅 `lan` 无 wan |
| 不集成 | `ppp` / `kmod-ppp` / `kmod-mppe`（无 PPPoE）、无线组件（`ENABLE_WIFI_K510=0`）、`luci-app-samba4`、`luci-app-filetransfer`、honk / doona |
| 产物名 | `openwrt_amlogic_s905d_k6.12.*_<日期>.img.gz`（ophub 生成，与 Release 名不同） |

### 晶晨宝盒在线更新

`/etc/config/amlogic` 已预置 6 项在线更新配置：固件 4 项 —— `firmware_repo = mackolzjj/N1-OpenWrt`、`firmware_tag = OpenWrt`、`firmware_suffix = .img.gz`、`kernel_branch = 6.12`（与 `6.12.y` 对齐）；内核 2 项 —— `kernel_path = mackolzjj/ophub-kernel-ftrace`、`kernel_tags = kernel_stable`。

> 这套配置与本库 Release 名天然匹配（`OpenWrt_main_日期` 含 `OpenWrt` 关键字），只要仓库有 Release，列表就有内容；上限 10 个。`kernel_path` / `kernel_tags` 属于内核在线更新，**已指向自编译内核仓库的 `kernel_stable`** —— 在 LuCI 点「在线更新内核」不会拉回 ophub 官方内核、不会丢掉 ftrace；前提是 `mackolzjj/ophub-kernel-ftrace` 的 `kernel_stable` Release 存在。

### 常见问题

| 现象 | 排查 |
| --- | --- |
| 在线更新列表为空 | 先确认仓库已发布 Release；再核对上述 6 项配置；列表上限 10 个 |
| `/sys/kernel/btf/vmlinux` 不存在 | 运行时内核由 ophub 打包时注入，BTF / ftrace 取决于自编译内核仓库的 `kernel_stable`；自行换过内核、刷错镜像或在 LuCI 更新成官方内核都会丢失，honk / dae 会直接退出 |
| `available_tracers` 只有 `nop` | 打包时拉回了未开 `FUNCTION_TRACER` 的官方内核；检查 workflow 的 `kernel_repo` 与 `kernel_stable` Release 里的 `6.12.x.tar.gz` |
| LuCI 无 honk / doona 菜单 | 设计如此，本线不内置；需设备端自装，或改刷 `Phicomm-N1_ImmortalWrt` |
| 晶晨宝盒「内核的下载仓库」显示 `ophub/kernel` | 打包阶段 `remake` 用 common-files 覆盖 `/etc/config/amlogic` 并 sed 改写 tag；本仓库的 `zz-amlogic-repo` 会在首次启动写回自建仓库。旧固件可手动 `uci set amlogic.config.amlogic_kernel_path=https://github.com/mackolzjj/ophub-kernel-ftrace && uci commit amlogic` |
| 切换主题后样式丢失 / 中文不生效 | 旧固件的 `/etc/config/luci` 把主题写成 `argon` / `bootstrap` 短名；本仓库已改为 `/luci-static/...` 绝对路径并把 `lang` 修正为 `zh_cn`，重刷即可 |
| 个别第三方页面仍是英文 | 固件 JS 比上游翻译新；`diy/po/` 下的补译 `.po` 由 `luci.mk` 编进对应中文 apk 包。新增文案时只改 `.po` 文本即可 |
| 无法拨号 / 无 WiFi | 设计如此，`.config` 明确禁用 ppp 与无线组件 |

### 自定义编译

`armsr/armv8/N1/.config`（内置包 / 内核选项 / 中文包符号）· `armsr/armv8/diy/diy.sh`（软件源 + 中文 feed 包）· `armsr/armv8/diy/po/`（补译源，纯文本）· `armsr/armv8/N1/files/`（预置 `/etc/config`、首次启动 uci-defaults：`zz-luci-argon-theme` / `zz-amlogic-repo` 与 crontabs）· `armsr/armv8/N1/mk_s905d_n1.sh`（本地打包）· `.github/workflows/armsr_armv8.yml`（触发、内核、Release 规则）。

改动后推送到 `main` / `master` 会触发构建；仅改文档且不想编译时，在 commit body 写 `[skip ci]`。

</details>

## 🙏 致谢

[OpenWrt](https://github.com/openwrt/openwrt) · [ophub/amlogic-s9xxx-openwrt](https://github.com/ophub/amlogic-s9xxx-openwrt) · [ophub/kernel](https://github.com/ophub/kernel) · [daeuniverse/openwrt-packages](https://github.com/daeuniverse/openwrt-packages) · [luci-app-podman](https://github.com/Zerogiven-OpenWRT-Packages/luci-app-podman)
