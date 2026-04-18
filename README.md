# 352 Air Purifier for Home Assistant

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)
![IoT Class](https://img.shields.io/badge/IoT_Class-Local_Push-success.svg)

专为 352 品牌智能空气净化器打造的 Home Assistant 局域网本地集成插件。
**脱离云端，毫秒级响应，完全本地局域网 UDP 控制！**

## ✨ 支持的型号 (Supported Models)
* 352 X83 (全尺寸空气净化器)
* 352 X50 (小巧版空气净化器)
* 352 X83C 可以同步状态，疑似没有本地UDP控制指令
* *(理论上支持采用相同协议的其他 352 设备)*

## 🚀 核心特性 (Features)
* ⚡ **完全本地化**：不依赖 352 官方云服务器，断网依然可用。
* ⚡ **毫秒级状态同步**：采用 UDP 广播/单播机制，状态秒级反馈。
* 🌬️ **风机控制**：支持开关机、1-6 档无极风速调节。
* 🎛️ **模式切换**：支持自动 (Auto)、睡眠 (Sleep)、极速 (Turbo)、手动 (Manual) 模式。
* 💡 **灯光控制**：屏幕灯光开关。
* 📊 **丰富传感器**：实时 PM2.5、滤芯安装状态。

## 📦 安装方法 (Installation)

### 推荐方法：通过 HACS 安装
1. 打开 Home Assistant，进入 HACS。
2. 点击右上角的三个点 `...` -> **自定义存储库 (Custom repositories)**。
3. 存储库 URL 填入：`https://github.com/yymonday/ha-352-airpurifier`
4. 类别选择：**集成 (Integration)**。
5. 点击添加后，在 HACS 中搜索 `352 Air Purifier` 并下载安装。
6. 重启 Home Assistant。

### 手动安装
1. 下载本仓库的代码。
2. 将 `custom_components/air_352_x83` 文件夹放入你 Home Assistant 根目录的 `custom_components` 文件夹中。
3. 重启 Home Assistant。

## ⚙️ 配置使用 (Configuration)
1. 在 Home Assistant 左侧菜单点击 **配置 (Settings)** -> **设备与服务 (Devices & Services)**。
2. 点击右下角 **添加集成 (Add Integration)**，搜索 `352`。
3. 在弹出的配置框中输入：
   * **设备型号 (Model)**: 选择 X83 或 X50
   * **设备 IP (Host)**: 填入净化器在局域网内的 IP (建议在路由器绑定静态 IP)
   * **设备 MAC 地址**: 净化器的 MAC 地址 (格式如 `00:95:69:D7:9B:FE`)
4. 提交后即可自动生成包含风扇、屏幕灯和多个传感器的单一设备卡片！

## 📝 贡献与支持
本项目通过逆向抓包 352 官方协议开发而成，我没有净水器设备所以没有添加云端部分协议，欢迎有能力的大佬补充！
