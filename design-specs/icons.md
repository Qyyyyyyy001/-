# Icons 图标库

> 来源 Figma 节点: `33:1971`（基础组件页 → `基础产品图标` section）
> 完整清单包含 **7 个分组共 370+ 个图标**。所有命名均直接来自源文件的 Figma instance 名。

图标在 Figma 中以独立组件库的形式存在；Pay B 端源文件中的图标都是对该组件库的 **instance** 引用。本仓库没有把实际 SVG 落地，复用时请从原 Figma 文件按需导出到 `design-specs/icons/<category>/`。

## 分组与前缀

| 分组 | Instance 命名前缀 | 典型尺寸 | 数量 | 备注 |
| --- | --- | ---: | ---: | --- |
| **Basic Product Icons** | `CEX_` | 24 px | 187 | 核心业务图标：交易、账户、设置、通知、充提币、KYC… |
| **Control Icons** | `CEX_` | 24 px | 50 | 控制/方向/状态填充类：箭头、chevron、add/subtract、filled status |
| **Header Icons** | `TwoColor_` | 24 px | 75 | 导航/Header 双色图标：活动中心、代理计划、Launchpool、各类交易入口… |
| **Social Media Icons** | `CEX_` | 24 px | 26 | 社交平台 + 浏览器/OS logo |
| **Common Currency Icons** | `Crypto_` | 28 px | 20 | 主流加密币种 logo |
| **Common Chain Icons** | `Chain_` | 20 px | 20 | 主流链 logo（含 `默认链图标` / `fill-all` 两个特殊项） |
| **Common Fiat Currency Icons** | (3 位国家代码) | 40 px | 52 | 法币 logo + `法币占位` |

完整命名列表可以在本文件的附录章节查看，也可以打开 target Figma 文件的 `Design System → Icons` 板直接查阅（每个图标用命名 cell 展示）。

## 使用规范

- **主图标色**：`Icon/Icon-Primary` `#303236`
- **次级图标色**：`Icon/Icon-Secondary` `#484B51`
- **三级图标色**：`Icon/Icon Tertiary` `#84888C`
- **反色/深底**：`var(--color-text-always-white)` `#FFFFFF`
- **品牌 accent**：`Header Icons (TwoColor_*)` 用品牌蓝 `#387CF2` 作为双色其中一色
- **币种/链/法币 logo**：**保留品牌色**，不要二次着色
- **推荐尺寸** 跟随按钮/列表的尺度：`12 / 14 / 16 / 18 / 20 / 24 / 28 / 40 px`

## 附录 — 完整图标清单

### 1. Basic Product Icons (`CEX_*`) · 187 个

Settings · Scan · Copy · Paste · Show · Hide · profile · Delete · Download · Edit · Pin · Unpin · Filter · Filtered · Notification · NotificationDisabled · Reminded · Subscribed · Language · Darkmode · Lightmode · OrderHistory · Deposit · Withdraw · BankCard · GateCard · Bot · Lianghuagendan · Earn · Gift · Borrow · Lending · RedPacket · Chat · Quick MSG · Fee · Qianbao&yue · SecuritySettings · ReplenishCollateral · Verified · UserSecurity · UmbrellaProtection · Transfer_Horizontal · Transfer_Vertical · Spot · Reserve Proof · Personal · Streamer · AccountSwitch · Gate account · Rebate · More_Horizontal · More_Vertical · Biaoqing · Convert · FaceRecognition · Fingerprint · gesture · Gatecode · Keyboard · SpotGrid · LeverageTrading · Future · Menu · EditGroup · MoveUpDown · Password · Unlock · Zhanghuxinxi · Jiazhao · Huzhao · Tutorial · Share · Like · Dislike · Service · Grid · P2P · Loop · Ascendingsort · Descendingsort · Calendar · Gif · DataCenter · Sound · Mute · AutoEarn · AutoInvest · Collateral · DualInvestment · KYCCertification · Translate · zuixiaohua · Maximize · Layout1 · Layout2 · Kline · OrderView_1 · OrderView_2 · OrderView_3 · Redup · Greendown · Colorpreferences · ChartView · LiveNow · FearinDex · Trend · Helcenter · Refresh · Note · ChartInterval · RotateScreen · KeyboardDelete · Space · EmojiFavorites · HardwareWallet · Bluetooth · Host · Top · UnTop · SimilarKLine · ApplyLive · Image · ImageLoadFailed · Quote · Analysis · AccountUpgrade · Video · StepbyStep · Borrowing · SpotRecharge · Points · A_Z_sort · Returetotrade · ChartDisplay · Return · Goldendog · FrontRunning · FutureGrid · TradeRanking · SurgeRanking · Coin · GainersRanking · LosersRanking · ParameterSettings · Home · SubAccounts · Api · Vouchers · Tickets · Camera · Mobile · PeopleCount · Attachment · LoanDetails · Fullscreen · Danmaku · CloseDanmaku · Sub Accounts · Log Out · PointCard · QR code · Passkey · DiagonalArrow · Link · Alpha · OnchainDeposit · OnchainWithdraw · BusinessIncome · Merchant · FiatDeposit · QuickBuy · Location · Puzzle · Address Book · Checker Flag · OrderDetails · GT Holding · Transaction History · Options account · BTC Future · Delivery Future · Bulk Transfer · Innovation · Coupon · Vip · Gate SimpleEarn

### 2. Control Icons (`CEX_*`) · 50 个

Iconplaceholder · Favorite · chevron_left · chevron_right · left_aligned arrow · right_aligned arrow · DoubleArrow_left · DoubleArrow_right · DoubleArrow_up · DoubleArrow_down · chevron_up · chevron_down · Search · close&orror · add · subtract · success · back arrow · ForwardArrow · GTE · LTE · circlefilled_add · circlefilled_subtract · circlefilled_error · circlefilled_info · circlefilled_warning · circlefilled_success · circlefilled_progress · hot_fill · rise_fill · fall_fill · down_fill · up_fill · pause · play · kuaijin · Text-fill · mp3-fill · mp4-fill · pdf-fill · DefaultAvatar · Avatar NoPadding · Corporate avatar · Clover · sort · btn loading · radio_inactive · btn loading2 · GTE input · LTE input

### 3. Header Icons (`TwoColor_*`) · 75 个

活动中心 · 代理计划 · 邀请返佣 · TG小程序 · 最新公告 · Gate商城 · VIP服务 · 储备金 · 机构服务 · 快捷交易 · 买币 · 卖币 · P2P · 法币定投 · GateCard · 动态 · 直播 · 热聊 · 未来事件 · Blog · 快讯 · 合约入门 · 学院 · 合作伙伴 · 现货交易 · 创新区 · 盘前交易 · 闪兑 · 杠杆交易 · 杠杆ETF · 跟单 · 机器人 · 永续合约 · 交割合约 · 期权 · 统一账户 · 帮助中心 · 合约活动 · 模拟交易 · Launchpool · Launchpad · CandyDrop · Web3Airdrop · HODLerAirdrop · 余币宝 · 理财宝 · 结构性理财 · 定投理财 · 双币宝 · 量化基金 · 抵押借币 · 法币理财 · 链上赚币 · GT挖矿 · BTC Staking · ETH2.0挖矿 · 财富管理 · 日历 · 广场 · 推荐 · 热门 · 深度 · 关注 · 行情分析 · 专题 · 区块链知识 · Grid · OTC · Premium Loan · Alpha · FiatDeposit · Broker · 资管业务 · VIP · Soft Staking · VIP wealth

### 4. Social Media Icons (`CEX_*`) · 26 个

Telegram · Twitter · Facebook · Youtube · Instagram · Github · Medium · Linkedin · Reddit · VK · Whatsapp · Discord · Wechat · Line · Zalo · google · microsoft · baipishu · metamask · Email · tiktok · Apple · Linux · Windows · Macos · DownloadApi

### 5. Common Currency Icons (`Crypto_*`) · 20 个

BTC · ETH · USDT · GT · LTC · XRP · BNB · SHIB · DOGE · SOL · AVAX · TRX · DOT · PIGCOIN · MEW · RADAR · ENA · Base · shouzimu · zhanwei

### 6. Common Chain Icons (`Chain_*`) · 20 个

默认链图标 · fill-all · BTC · ETH · USDT · GT · LTC · XRP · BNB · SHIB · DOGE · SOL · AVAX · TRX · DOT · PIGCOIN · MEW · RADAR · ENA · Base

### 7. Common Fiat Currency Icons · 52 个

CNY · VND · USD · INR · TRY · NGN · PKR · BDT · PHP · GBP · IDR · ZAR · EGP · UZS · TWD · HKD · GHS · VES · UAH · RUB · EUR · BRL · JPY · MYR · PLN · SAR · ARS · AED · KZT · THB · XAF · XOF · PGK · KES · MAD · BYN · AUD · TZS · SEK · AZN · COP · HUF · MXN · RON · AMD · DZD · NPR · JOD · CLP · IQD · MRU · 法币占位
