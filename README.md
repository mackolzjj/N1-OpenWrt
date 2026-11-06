<div align="center">

# Phicomm N1 · OpenWrt 25.12

**官方 OpenWrt 源码编译 + ophub 打包 + 自编译内核**，面向斐讯 N1（s905d）的有线旁路由固件。

[![Build](https://github.com/mackolzjj/N1-OpenWrt/actions/workflows/armsr_armv8.yml/badge.svg)](https://github.com/mackolzjj/N1-OpenWrt/actions/workflows/armsr_armv8.yml)
[![Release](https://img.shields.io/github/v/release/mackolzjj/N1-OpenWrt?label=Release)](https://github.com/mackolzjj/N1-OpenWrt/releases)
![Source](https://img.shields.io/badge/OpenWrt-v25.12.6-orange)
![Kernel](https://img.shields.io/badge/kernel-6.12.y-blue)
![Board](https://img.shields.io/badge/board-s905d%20%2F%20armsr--armv8-green)
![Package](https://img.shields.io/badge/pkg-apk-lightgrey)

</div>

> **定位**：拨号和 WiFi 交给主路由，本固件不集成 PPPoE / 无线驱动，**也不内置 honk / dae / doona** —— 它只把 eBPF / BTF / ftrace / NFQUEUE 内核底座准备好，透明代理请自行在设备端安装。

---

## 一、这个仓库做什么

GitHub Actions 从 OpenWrt 官方 `v25.12.6` 源码编译 `armsr/armv8` 的 `rootfs.tar.gz`，再用 `ophub/amlogic-s9xxx-openwrt` 打包成 N1 可写入 U 盘的 `.img.gz`。**打包阶段会把运行内核整体替换成本仓库指定的自编译内核**。

```text
openwrt/openwrt @ v25.12.6
  + armsr/armv8/N1/.config          （包选择、内核符号、中文包开关）
  + armsr/armv8/diy/diy.sh          （第三方 feed 与简体中文翻译源）
  + armsr/armv8/N1/files/           （预置 /etc 配置与首次启动脚本）
        │  make defconfig / download / make
        ▼
  openwrt-armsr-armv8-generic-rootfs.tar.gz
        │  ophub/amlogic-s9xxx-openwrt（s905d，256/1024，注入自编译内核）
        ▼
  openwrt_amlogic_s905d_k6.12.x_YYYY.MM.DD.img.gz  →  Release
```

本仓库自包含整套构建配置，构建时只依赖 OpenWrt 官方源码与第十节列出的上游仓库。

## 二、为什么换自编译内核

ophub 官方内核未开 ftrace，honk 会报 `udp_trace_unavailable`（UDP 流程缺内核路由信息）。内核仓库 [`mackolzjj/ophub-kernel-ftrace`](https://github.com/mackolzjj/ophub-kernel-ftrace) 在 `kernel-config/release/stable/config-6.12` 里打开/固定了这些项，并发布到 Release tag `kernel_stable`（当前资产 `6.12.115.tar.gz`）：

| 用途 | 内核选项 |
| --- | --- |
| BPF trampoline / fentry（honk UDP trace） | `CONFIG_FUNCTION_TRACER=y`、`CONFIG_DYNAMIC_FTRACE=y` |
| eBPF / BTF | `CONFIG_DEBUG_INFO_BTF=y`、`CONFIG_BPF_JIT=y`（提供 `/sys/kernel/btf/vmlinux`） |
| NFQUEUE 支持（`nft queue` / `nfnetlink_queue` 直接编进内核） | `CONFIG_NETFILTER_NETLINK=y`、`CONFIG_NETFILTER_NETLINK_QUEUE=y`、`CONFIG_NF_TABLES=y`、`CONFIG_NFT_QUEUE=y` |

> ⚠️ **别看错地方**：`armsr/armv8/N1/.config` 里的 `CONFIG_KERNEL_*` 只作用于 OpenWrt 自身编译出来的产物；**最终运行内核是打包阶段注入的**，选项以上面那份 `config-6.12` 为准。`kernel_repo` / `kernel_usage: stable` / `openwrt_kernel: 6.12.y` / `auto_kernel: true` 写在 workflow 的 `Package N1 firmware` 步骤里。

刷机后用这段确认内核没被换回官方版本：

```sh
uname -r                                                    # 6.12.x-ophub
ls -l /sys/kernel/btf/vmlinux                                # 必须存在
cat /sys/kernel/debug/tracing/available_tracers              # 应含 function / function_graph，不能只有 nop
grep -E 'CONFIG_(FUNCTION_TRACER|DYNAMIC_FTRACE)=y' /boot/config-*   # 两行都要有输出
uci show amlogic.config | grep -E 'firmware|kernel_'          # 在线更新源应指向自建仓库
```

## 三、固件默认状态

以下每一项都能在仓库文件里找到对应来源，没有写在文件里的行为就是 OpenWrt / ophub 上游默认。

| 项目 | 默认值 | 来源 |
| --- | --- | --- |
| 系统 / 架构 | OpenWrt `25.12.6`、`armsr/armv8`、`apk` 包管理 | `REPO_TAG`、`.config` |
| Web 管理 | `luci` + `uhttpd` + `uhttpd-mod-ubus`，HTTP `192.168.2.2` | `.config`、`files/etc/config/network` |
| 登录 | 用户 `root`，**空密码** | 仓库未预置密码；见下方说明 |
| 语言 | `lang=zh_cn`，语言列表含 `en (English)` 可切回英文 | `files/etc/config/luci` |
| 主题 | Argon，`/luci-static/argon` 等 4 个绝对路径 | `files/etc/config/luci`、`zz-luci-argon-theme` |
| 中文包 | 6 个 `luci-i18n-*-zh-cn`：`base` / `firewall` / `package-manager` / `amlogic` / `podman` / `argon-config` | `.config` + `diy.sh` |
| 补译 | `amlogic-extra.po`（17 条）、`podman-extra.po`（9 条），由 `luci.mk` 编成额外 `.lmo` 打进对应中文包 | `diy/po/`、`diy.sh` |
| 内置应用 | `luci-app-amlogic`（晶晨宝盒）、`luci-app-podman` + `podman` | `.config` |
| 网络 | `eth0` 静态 `192.168.2.2/24`，网关 `192.168.2.1`，仅 `lan` 无 `wan`；**未配置 DNS** | `files/etc/config/network` |
| 禁用 | `ppp` / `kmod-ppp` / `kmod-mppe`、`luci-app-samba4`、`luci-app-filetransfer`、大量无关网卡 `kmod-*`、`initramfs` / `ext4` / `squashfs` 镜像 | `.config` |
| 镜像格式 | 只出 `rootfs.tar.gz`（`CONFIG_TARGET_ROOTFS_TARGZ=y`），供 ophub 打包 | `.config` |
| eBPF 配套 | `vmlinux-btf-builtin`；`CONFIG_KERNEL_BPF_EVENTS` / `DEBUG_INFO_BTF` / `XDP_SOCKETS` = y | `diy.sh` 接入 daeuniverse feed、`.config` |
| 时区 | `timezone=CST-8`、`zonename=Asia/Shanghai`，`zoneinfo-asia`，每日 04:00（北京时间）`fstrim -a` | `zz-system-timezone`、`files/etc/crontabs/root`、`.config` |
| 单臂旁路由内核参数 | 关闭 `send_redirects` 与 `rp_filter`（`all` / `default` / `eth0`） | `files/etc/sysctl.d/60-honk-single-arm.conf` |
| 在线更新源 | 固件仓库 `mackolzjj/N1-OpenWrt`、内核仓库 `mackolzjj/ophub-kernel-ftrace`，详见第六节 | `zz-amlogic-repo` |
| 日常工具 | `bsdtar`、`btrfs-progs`(+zstd)、`f2fs-tools`、`xfs-fsck`/`xfs-mkfs`、`pigz`、`tar`、`gawk`、`getopt`、`perl-*`、`chattr`/`lsattr`、`fstrim`、`zoneinfo-asia` | `.config` |

**关于密码**：仓库里没有任何设置 root 密码的文件，所以固件沿用 OpenWrt 默认 —— **root 空密码**，LuCI 会提示尚未设置密码。Release 说明里那句 `密码: password` 是 workflow 里写死的模板文字，**不是实际密码**，请勿照抄。

**关于 bootloader**：仓库不再预置 `files/etc/config/amlogic`（会被 ophub 打包默认值覆盖，且其 `amlogic_write_bootloader='1'` 会在安装/更新时把主线 u-boot `dd` 进 eMMC 引导区）。`zz-amlogic-repo` 只写更新源、不碰这一项，实际值由 ophub 提供 `0`，即保留原厂 bootloader。U 盘启动和安装到 eMMC 均不受影响。

## 四、下载与刷机

1. 在 [Releases](https://github.com/mackolzjj/N1-OpenWrt/releases) 取 `openwrt_amlogic_s905d_k6.12.*_*.img.gz`，解压写 U 盘。若 Releases 为空，说明还没有成功发布过镜像，去 Actions 手动跑一次（见第六节）。
2. U 盘启动 N1，浏览器打开 `http://192.168.2.2`，用户 `root`，密码留空。
3. 需要固化到 eMMC 时，在 U 盘系统里执行 `openwrt-install-amlogic`。N1 的常规做法是不改写引导区（上游脚本示例用 `no` 参数：保留原厂 bootloader + `/boot/u-boot.ext` 引导）；本仓库没有、也不需要改动这个开关。

> 建议**全新刷写、不保留配置**：三个 `zz-*` 首次启动脚本只在 `/etc/uci-defaults` 被首次执行时生效，保留旧配置升级不会补写主题、时区和在线更新源。

## 五、首次启动后必须手动处理

以下几项目前**没有固化**（属于已知遗留项），全新刷机后建议先处理：

```sh
# 1) 补 DNS：预置 network 只有 IP/网关，没有上游 DNS，apk update 等设备端联网操作可能解析不了域名
uci add_list network.lan.dns='223.5.5.5'
uci commit network

# 2) 关掉 LAN 的 DHCP / DHCPv6 / RA：旁路由接在主路由 LAN 上会出现两个 DHCP 服务器
uci set dhcp.lan.ignore='1'
uci set dhcp.lan.dhcpv6='disabled'
uci set dhcp.lan.ra='disabled'
uci commit dhcp

# 3) 设置密码，然后重启让网络生效（network restart 会掐断当前 SSH）
passwd
reboot
```

需要 honk / dae 时自行按架构安装；装之前先跑第二节的验证命令，确认 BTF 与 ftrace 都在。单臂旁路由还可能要按实际拓扑调整 `/etc/config/firewall` 与 honk 的 `config.dae`（DNS 自环要用 `direct(must)` 类规则放行）。

## 六、构建与发布

### 触发方式

| 方式 | 说明 |
| --- | --- |
| 手动 | Actions → `Build OpenWrt-25.12 for armsr_armv8` → **Run workflow**（最干净，不用造 commit） |
| push | `main` / `master` 分支的提交自动触发；提交信息（标题或正文）含 `[skip ci]` 时 GitHub Actions 会跳过本次 push 构建 |
| 定时 | `cron: 0 0 1,16 * *`，GitHub Actions 按 **UTC** 解析，即每月 1、16 日北京时间 08:00 |

同一分支的并发构建会取消前一个（`concurrency` + `cancel-in-progress`）。Runner 为 `ubuntu-24.04`，`permissions: contents: write` 用于创建 Release。

### 13 个步骤

| # | 步骤 | 关键点 |
| --- | --- | --- |
| 1 | `actions/checkout@v6.0.3` | 固定 tag，不用可变分支 |
| 2 | Free up disk space | 删除 runner 预装 SDK，腾 10~15GB |
| 3 | Initialize environment | 编译依赖全部固化在 workflow 内，`TZ=Asia/Shanghai` |
| 4 | `actions/cache@v6` | 按 `github.ref` 缓存 `~/.ccache`；`.config` 里 `CONFIG_CCACHE=y`，编译上限 5G |
| 5 | Clone source code | clone `openwrt/openwrt` 后 checkout tag `v25.12.6`，生成 `FILE_DATE` |
| 6 | Update & Install feeds | `feeds update -a` → `diy.sh` → 再 `feeds update -a` → `feeds install -a`（第二次更新不会清掉注入的 `.po`） |
| 7 | Load N1 custom config | 把 `armsr/armv8/N1/files` 与 `.config` 移进 openwrt 源码树 |
| 8 | Download package | `make defconfig` → **中文包检查** → `make download -j(nproc*2)` |
| 9 | 安装 bpf-linker | 下载 v0.13.0 静态包；本线不编译 honk，属保留步骤，但下载失败会中断构建 |
| 10 | Compile N1 firmware | `make -j(nproc+1)`，失败则 `make -j1 V=s` 重跑并输出详细日志 |
| 11 | Package N1 firmware | `ophub/amlogic-s9xxx-openwrt@main`，参数见下表 |
| 12 | Upload firmware to release | 创建/复用 Release tag，上传 `*.img.gz`（`--clobber` 覆盖同名资产） |
| 13 | Delete old releases | 只保留最近 10 个 Release tag |

**🔴 第 8 步必须人工看一眼**：日志里 `== 已启用的简体中文翻译包 ==` 下面应列出 **6 行** `CONFIG_PACKAGE_luci-i18n-*-zh-cn=y`。当前检查只发 `::warning::`、**不会让构建失败**（上次固件缺中文包就是这么漏过去的）。如果只看到 warning，不要刷机。

### 打包参数

| 输入 | 值 |
| --- | --- |
| `openwrt_path` | `openwrt/bin/targets/armsr/armv8/*rootfs.tar.gz` |
| `openwrt_board` / `openwrt_size` / `builder_name` | `s905d` / `256/1024` / `Mackol` |
| `kernel_repo` / `kernel_usage` | `mackolzjj/ophub-kernel-ftrace` / `stable` |
| `openwrt_kernel` / `auto_kernel` | `6.12.y` / `true` |
| `openwrt_ip` | **不设置**。LAN IP 由 `files/etc/config/network` 决定，ophub `remake` 只在没有预置 network 配置时才改 `config_generate`，传了这个值也不生效 |

`diy.sh` 做四件事：clone `daeuniverse/openwrt-packages`（只取 `vmlinux-btf-builtin`）、`ophub/luci-app-amlogic`、`Zerogiven-OpenWRT-Packages/luci-app-podman`、`jerrykuku/luci-theme-argon`；移除 `luci-app-attendedsysupgrade`；校验并补齐三个包目录的 `po/zh_Hans`；把 `diy/po/*-extra.po` 注入同一目录。中文翻译**只有这一条路径** —— 由 `luci.mk` 扫描 `po/zh_Hans/*.po` 生成 `.lmo` 并打进 `luci-i18n-*-zh-cn` 包，仓库内不含二进制 `.lmo`，也没有构建期手工复制步骤。

### 产物与 Release

- 镜像：由 ophub 生成的 `openwrt_amlogic_s905d_k6.12.<版本>_<打包日期>.img.gz`，例如 `openwrt_amlogic_s905d_k6.12.115_2026.11.06.img.gz`。
- Release tag：`OpenWrt_<分支>_<YYYYMMDD>`（如 `OpenWrt_main_20261106`）。同日重复构建复用同一 tag，`gh release create` 失败被忽略，上传时 `--clobber` 覆盖同名镜像。
- tag 中的 `OpenWrt` 关键字与晶晨宝盒的 `firmware_tag='OpenWrt'` 匹配，在线更新列表才有内容；列表上限 10 个。

### 晶晨宝盒在线更新

ophub 打包时会用自带 `common-files/etc/config/amlogic` 覆盖静态模板并 `sed` 改写 tag，所以**不能靠预置配置文件**。首次启动脚本 `zz-amlogic-repo` 写回 6 项：

| 项 | 值 |
| --- | --- |
| `amlogic_firmware_repo` | `https://github.com/mackolzjj/N1-OpenWrt` |
| `amlogic_firmware_tag` / `amlogic_firmware_suffix` | `OpenWrt` / `.img.gz` |
| `amlogic_kernel_branch` | `6.12` |
| `amlogic_kernel_path` | `https://github.com/mackolzjj/ophub-kernel-ftrace` |
| `amlogic_kernel_tags` | `kernel_stable` |

这样在 LuCI 点「在线更新内核」不会拉回 ophub 官方内核、不会丢掉 ftrace / BTF / NFQUEUE。前提是内核仓库的 `kernel_stable` Release 里存在 `6.12.x.tar.gz`。

## 七、仓库文件地图

| 路径 | 作用 |
| --- | --- |
| `.github/workflows/armsr_armv8.yml` | 唯一的构建流水线：触发、依赖、feeds、编译、打包、Release |
| `README.md` | 本文件 |
| `armsr/armv8/N1/.config` | 目标、包选择、内核符号、6 个中文包开关、`rootfs.tar.gz`、`ccache` |
| `armsr/armv8/N1/files/etc/config/luci` | 默认语言 `zh_cn`、Argon 主题、4 个绝对路径主题 |
| `armsr/armv8/N1/files/etc/config/network` | `eth0` 静态 IP / 网关 / packet steering |
| `armsr/armv8/N1/files/etc/crontabs/root` | 每日 04:00 `fstrim -a` |
| `armsr/armv8/N1/files/etc/sysctl.d/60-honk-single-arm.conf` | 单臂旁路由关闭 ICMP 重定向与反向路径过滤 |
| `armsr/armv8/N1/files/etc/uci-defaults/zz-luci-argon-theme` | 首次启动锁定 Argon 与 4 个主题路径 |
| `armsr/armv8/N1/files/etc/uci-defaults/zz-amlogic-repo` | 首次启动写回 6 项在线更新源 |
| `armsr/armv8/N1/files/etc/uci-defaults/zz-system-timezone` | 首次启动写回 `CST-8` / `Asia/Shanghai`，重载 system 与 cron |
| `armsr/armv8/diy/diy.sh` | 接入 4 个第三方 feed、移除 attendedsysupgrade、注入中文 po |
| `armsr/armv8/diy/po/amlogic-extra.po`、`podman-extra.po` | 上游未收录文案的补译（纯文本，无 fuzzy 条目） |
| `armsr/armv8/N1/mk_s905d_n1.sh` | 上游模板保留的**本地**打包脚本（`ENABLE_WIFI_K510=0` 等参数在这里）；它依赖 `make.env`、`public_funcs` 和大量 `files/` 补丁文件，本仓库均未提供，**GitHub Actions 构建完全不使用它** |

三个 `zz-*` 脚本以 `zz-` 开头，按字典序排在 `/etc/uci-defaults` 所有脚本之后执行，`exit 0` 后由 `/etc/init.d/boot` 删除，只在首次启动生效一次；之后用户可在 LuCI 自由修改。时区用首次启动脚本而不是预置 `/etc/config/system`，是因为 `bin/config_generate` 发现该文件非空就会跳过生成 hostname、NTP `timeserver` 等默认配置。

## 八、已知限制

- **不内置 honk / dae / doona**，也没有 PPPoE 与 WiFi；需要请自行安装或改刷其他固件。
- 中文包检查只是 warning；`diy.sh` 的 `po/zh_Hans` 校验同样只告警。构建日志必须人工确认。
- 第三方 feed 用 `git clone --depth=1` 拉默认分支，**未锁定版本**，上游改目录结构或新增依赖可能影响构建（例如 Argon 主题更新）。
- `bpf-linker` 步骤对本线无实际用途，但其下载是构建的单点依赖。
- `files/etc/config/network` 没有 DNS、`/etc/config/dhcp` 未预置 → 首次启动需按第五节手动补 DNS 并关闭 DHCP。
- 首次启动脚本只在全新刷机时执行；保留配置升级不会自动修正主题、时区、在线更新源。
- Release 说明中的 `密码: password` 是模板文字，实际为空密码。
- 本 README 描述的是 `main` 分支**源码**状态；镜像是否包含某项改动，以该次构建的日志为准。改动后需要重新 `Run workflow` 才会进入固件。

## 九、自定义

| 想改什么 | 改哪里 |
| --- | --- |
| 增删软件包、内核符号、镜像格式 | `armsr/armv8/N1/.config` |
| 接入新 feed / 插件、调整中文翻译 | `armsr/armv8/diy/diy.sh`、`armsr/armv8/diy/po/` |
| 默认 IP、网关、DNS、旁路由 sysctl | `armsr/armv8/N1/files/etc/config/network`、`files/etc/sysctl.d/` |
| 默认语言、主题、在线更新源、时区 | `armsr/armv8/N1/files/etc/config/luci` 与 `files/etc/uci-defaults/zz-*` |
| 触发方式、内核来源、Release 规则 | `.github/workflows/armsr_armv8.yml` |

改完推送到 `main` / `master` 即触发构建；只改文档且不想编译时，在提交信息里写 `[skip ci]`。**对 `files/` 和 `.config` 的改动只有重新构建固件后才会生效**，不会作用于已刷机的设备。

## 十、致谢

[OpenWrt](https://github.com/openwrt/openwrt) · [ophub/amlogic-s9xxx-openwrt](https://github.com/ophub/amlogic-s9xxx-openwrt) · [ophub/kernel](https://github.com/ophub/kernel) · [daeuniverse/openwrt-packages](https://github.com/daeuniverse/openwrt-packages) · [ophub/luci-app-amlogic](https://github.com/ophub/luci-app-amlogic) · [jerrykuku/luci-theme-argon](https://github.com/jerrykuku/luci-theme-argon) · [Zerogiven-OpenWRT-Packages/luci-app-podman](https://github.com/Zerogiven-OpenWRT-Packages/luci-app-podman)
