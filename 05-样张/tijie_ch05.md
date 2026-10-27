## 第 5 章　核反应与截面

<div class="work">
<p class="tag">题 5-1　掺硼量</p>
<p class="q"><span class="lab">问题</span>热中子在纯石墨里平均要走 32.6 m 才被吸收。若想把这段行程压到 1 m，每立方厘米石墨里要掺进多少硼-10？折成天然硼又是多少？</p>
<p class="given"><span class="lab">已知</span>$\lambda=1\ \mathrm{m}=100$ cm，$\Sigma_a=3.07\times10^{-4}\ \mathrm{cm^{-1}}$，$\sigma_a=3840$ b，$\rho=1.75\ \mathrm{g/cm^3}$，$M_{\mathrm{B}}=10.01\ \mathrm{g/mol}$，$N_A=6.022\times10^{23}$</p>
<div class="steps">
<div class="step"><span class="eq">$\Sigma_{\text{总}}=1/100=0.01\ \mathrm{cm^{-1}}$</span><span class="lead"></span><span class="say">1 m 对应的总截面</span></div>
<div class="step"><span class="eq">$\Sigma_{\mathrm{B}}=0.01-0.000307$</span><span class="lead"></span><span class="say">扣掉石墨自身的吸收</span></div>
<div class="step ind"><span class="eq">$\Sigma_{\mathrm{B}}=9.69\times10^{-3}\ \mathrm{cm^{-1}}$</span><span class="lead"></span><span class="say">硼要补的那一份</span></div>
<div class="step"><span class="eq">$N_{\mathrm{B}}=\Sigma_{\mathrm{B}}/(3840\times10^{-24})$</span><span class="lead"></span><span class="say">宏观截面除以单个核</span></div>
<div class="step ind"><span class="eq">$N_{\mathrm{B}}=2.5\times10^{18}\ \mathrm{cm^{-3}}$</span><span class="lead"></span><span class="say">折成每立方厘米个数</span></div>
<div class="step"><span class="eq">$m_{\mathrm{B}}=2.5\times10^{18}\times10.01/N_A=4.2\times10^{-5}$ g</span><span class="lead"></span><span class="say">每立方厘米的硼质量</span></div>
<div class="step"><span class="eq">$4.2\times10^{-5}/1.75=2.4\times10^{-5}$</span><span class="lead"></span><span class="say">除密度，得质量分数 $24\times10^{-6}$</span></div>
<div class="step ind"><span class="eq">$24\times10^{-6}/0.199=120\times10^{-6}$</span><span class="lead"></span><span class="say">再折成天然硼</span></div>
</div>
<p class="a"><span class="lab">答</span>$^{10}\mathrm{B}$ 的质量分数要掺到 $24\times10^{-6}$；折成天然硼约 $120\times10^{-6}$，因为天然硼里只有 19.9% 是 $^{10}\mathrm{B}$。32.6 m 就此被压到 1 m——石墨的纯度要求为什么苛刻到 $10^{-6}$ 量级，这道题就是答案。</p>
</div>

<div class="work">
<p class="tag">题 5-2　锂-6 放能</p>
<p class="q"><span class="lab">问题</span>写出 $^{6}\mathrm{Li}(n,\alpha)$ 的完整反应式，逐条核对电荷数与核子数，判断它放能还是吸能，并算出两个产物各分到多少动能。</p>
<p class="given"><span class="lab">已知</span>$^{6}\mathrm{Li}$ 6.0151228 u，n 1.0086649 u，$^{4}\mathrm{He}$ 4.0026033 u，$^{3}\mathrm{H}$ 3.0160493 u，$931.5\ \mathrm{MeV/u}$</p>
<div class="steps">
<div class="step"><span class="eq">$3+0=2+1=3$</span><span class="lead"></span><span class="say">电荷数两边相等</span></div>
<div class="step"><span class="eq">$6+1=4+3=7$</span><span class="lead"></span><span class="say">核子数也平</span></div>
<div class="step"><span class="eq">$6.0151228+1.0086649=7.0237877$ u</span><span class="lead"></span><span class="say">反应物质量相加</span></div>
<div class="step"><span class="eq">$4.0026033+3.0160493=7.0186526$ u</span><span class="lead"></span><span class="say">产物质量相加</span></div>
<div class="step"><span class="eq">$7.0237877-7.0186526=0.0051352$ u</span><span class="lead"></span><span class="say">前减后得质量差</span></div>
<div class="step"><span class="eq">$Q=0.0051352\times931.5=4.783$ MeV</span><span class="lead"></span><span class="say">乘 931.5 换成能量</span></div>
<div class="step"><span class="eq">$4.783\times4.0026/7.0187=2.73$ MeV</span><span class="lead"></span><span class="say">$^{3}\mathrm{H}$ 分到的动能</span></div>
<div class="step ind"><span class="eq">$4.783\times3.0160/7.0187=2.06$ MeV</span><span class="lead"></span><span class="say">α 分到的动能</span></div>
</div>
<p class="a"><span class="lab">答</span>反应式 $^{6}_{3}\mathrm{Li}+^{1}_{0}\mathrm{n}\to^{4}_{2}\mathrm{He}+^{3}_{1}\mathrm{H}$，即 $^{6}\mathrm{Li}(n,\alpha)^{3}\mathrm{H}$；电荷与核子数都平，$Q=+4.783$ MeV，放能。两个产物动量大小相等，轻的拿得多：$^{3}\mathrm{H}$ 拿 2.73 MeV，$^{4}\mathrm{He}$ 拿 2.06 MeV——探测器量到的正是这两个带电粒子，所以锂-6 玻璃能把“有没有中子”变成一个干净的信号。</p>
</div>

<div class="work">
<p class="tag">题 5-3　掺硼石墨</p>
<p class="q"><span class="lab">问题</span>一块石墨里掺了质量分数 $50\times10^{-6}$ 的天然硼（$^{10}\mathrm{B}$ 丰度 19.9%）。热中子的吸收平均自由程变成多少？比纯石墨的 32.6 m 短几倍？</p>
<p class="given"><span class="lab">已知</span>天然硼质量分数 $50\times10^{-6}$，丰度 0.199，$\rho=1.75\ \mathrm{g/cm^3}$，$M_{\mathrm{B}}=10.0129\ \mathrm{g/mol}$，$\Sigma_a=3.07\times10^{-4}\ \mathrm{cm^{-1}}$，$\sigma_a(^{10}\mathrm{B})=3840$ b，$N_A=6.022\times10^{23}$</p>
<div class="steps">
<div class="step"><span class="eq">$50\times10^{-6}\times0.199=9.95\times10^{-6}$</span><span class="lead"></span><span class="say">$^{10}\mathrm{B}$ 的质量分数</span></div>
<div class="step"><span class="eq">$N_{10}=\dfrac{9.95\times10^{-6}\times1.75}{10.0129}N_A$</span><span class="lead"></span><span class="say">质量分数换成数密度</span></div>
<div class="step ind"><span class="eq">$N_{10}=1.05\times10^{18}\ \mathrm{cm^{-3}}$</span><span class="lead"></span><span class="say">每立方厘米的 $^{10}\mathrm{B}$</span></div>
<div class="step"><span class="eq">$1.05\times10^{18}\times3840\times10^{-24}=4.02\times10^{-3}$</span><span class="lead"></span><span class="say">硼贡献的宏观截面</span></div>
<div class="step"><span class="eq">$3.07\times10^{-4}+4.02\times10^{-3}=4.33\times10^{-3}$</span><span class="lead"></span><span class="say">两项相加得总截面</span></div>
<div class="step ind"><span class="eq">$\lambda=1/4.33\times10^{-3}=231$ cm</span><span class="lead"></span><span class="say">倒过来就是 2.31 m</span></div>
<div class="step"><span class="eq">$32.6/2.31=14$</span><span class="lead"></span><span class="say">与纯石墨相比</span></div>
</div>
<p class="a"><span class="lab">答</span>掺质量分数 $50\times10^{-6}$ 的天然硼后，吸收平均自由程只有 2.31 m，比纯石墨的 32.6 m 短了 14 倍。其中 $^{10}\mathrm{B}$ 的质量分数才 $10\times10^{-6}$，石墨“散射多、吸收少”的优势就被砍掉一个数量级——核级石墨要求硼当量在 $1\times10^{-6}$ 以下，原因就是这个杠杆：3840 b 对 0.0035 b，差 $10^6$ 倍。</p>
</div>

<div class="work">
<p class="tag">题 5-4　铍中子源</p>
<p class="q"><span class="lab">问题</span>用 $Q$ 值公式验证 $^{9}\mathrm{Be}(\alpha,n)^{12}\mathrm{C}$ 的 $Q=+5.70$ MeV；镅-241 放出的 5.486 MeV α 打上去，为什么不用加速器就能出中子？</p>
<p class="given"><span class="lab">已知</span>$^{9}\mathrm{Be}$ 9.0121831 u，$^{4}\mathrm{He}$ 4.0026033 u，$^{12}\mathrm{C}$ 12.0000000 u，n 1.0086649 u，$E_\alpha=5.486$ MeV，$ke^2=1.44\ \mathrm{MeV\cdot fm}$</p>
<div class="steps">
<div class="step"><span class="eq">$9.0121831+4.0026033=13.0147864$ u</span><span class="lead"></span><span class="say">反应物质量相加</span></div>
<div class="step"><span class="eq">$12.0000000+1.0086649=13.0086649$ u</span><span class="lead"></span><span class="say">产物质量相加</span></div>
<div class="step"><span class="eq">$13.0147864-13.0086649=0.0061215$ u</span><span class="lead"></span><span class="say">前减后得质量差</span></div>
<div class="step"><span class="eq">$Q=0.0061215\times931.5=5.702$ MeV</span><span class="lead"></span><span class="say">乘 931.5 换成能量</span></div>
<div class="step"><span class="eq">$R=1.2(4^{1/3}+9^{1/3})=4.4$ fm</span><span class="lead"></span><span class="say">两核接触时的距离</span></div>
<div class="step ind"><span class="eq">$V_C=2\times4\times1.44/4.4=2.6$ MeV</span><span class="lead"></span><span class="say">库仑势垒高度</span></div>
</div>
<p class="a"><span class="lab">答</span>$Q=+5.702$ MeV，放能，没有阈能。但“没有阈能”不等于“随便就能发生”，还有 2.6 MeV 的库仑势垒要过；镅-241 的 α 有 5.486 MeV，高出势垒一倍多，穿过去的概率不小。把镅和铍磨细、压在一起，α 就会自己打进铍核，中子源源不断地出来：不用加速器、不用电，一个密封金属罐就是一台中子源。</p>
</div>

<div class="work">
<p class="tag">题 5-5　铀中行程</p>
<p class="q"><span class="lab">问题</span>若铀-238 的截面只有几何截面 1.74 b，铀金属中热中子的平均自由程是多少？按实际俘获截面 2.683 b 算又是多少？再把 6.673 eV 共振峰上的 22200 b 代进去，结果说明了什么？</p>
<p class="given"><span class="lab">已知</span>$\rho=19.05\ \mathrm{g/cm^3}$，$M=238.05\ \mathrm{g/mol}$，$N_A=6.022\times10^{23}$，三个截面 1.74 b、2.683 b、22200 b</p>
<div class="steps">
<div class="step"><span class="eq">$N=\dfrac{19.05}{238.05}\times6.022\times10^{23}$</span><span class="lead"></span><span class="say">先算原子数密度</span></div>
<div class="step ind"><span class="eq">$N=4.82\times10^{22}\ \mathrm{cm^{-3}}$</span><span class="lead"></span><span class="say">每立方厘米的铀核</span></div>
<div class="step"><span class="eq">$\Sigma=1.74\times10^{-24}\times4.82\times10^{22}=8.4\times10^{-2}$</span><span class="lead"></span><span class="say">按几何截面算</span></div>
<div class="step ind"><span class="eq">$\lambda=1/8.4\times10^{-2}=11.9$ cm</span><span class="lead"></span><span class="say">几何尺寸给的行程</span></div>
<div class="step"><span class="eq">$\Sigma=2.683\times10^{-24}\times4.82\times10^{22}=0.129$</span><span class="lead"></span><span class="say">换成实测俘获截面</span></div>
<div class="step ind"><span class="eq">$\lambda=1/0.129=7.7$ cm</span><span class="lead"></span><span class="say">真实俘获给的行程</span></div>
<div class="step"><span class="eq">$\Sigma=22200\times10^{-24}\times4.82\times10^{22}=1070$</span><span class="lead"></span><span class="say">再换成共振峰截面</span></div>
<div class="step ind"><span class="eq">$\lambda=1/1070=9.3\times10^{-4}$ cm</span><span class="lead"></span><span class="say">合 9.3 μm，约三万层</span></div>
</div>
<p class="a"><span class="lab">答</span>三处读数：几何截面给 11.9 cm，实际热中子俘获给 7.7 cm，共振峰上只有 9.3 μm。几何值与真实值只差一倍半，说明热中子区铀的俘获并不离奇，真正夸张的是硼-10 那一万八千倍；而到 6.673 eV 峰上，中子走 9.3 μm 就被吃掉，几毫米厚的燃料只有表面一层“看得见”这批中子——共振自屏蔽，就是这三种读数摆在一起才看出来的。附带一个对比：金属铀的原子数密度（$4.82\times10^{22}$）比石墨的 $8.77\times10^{22}$ 还低一半，但每个核的截面大得多，所以照样挡得住中子。</p>
</div>

<div class="work">
<p class="tag">题 5-6　冷却中子</p>
<p class="q"><span class="lab">问题</span>石墨中热中子（0.0253 eV）的 $\lambda_a=32.6$ m。0.001 eV 与 1 eV 时 $\lambda_a$ 各是多少？为什么“冷却中子”会让它更容易被吸收？</p>
<p class="given"><span class="lab">已知</span>$\lambda_a(0.0253\ \mathrm{eV})=32.6$ m，$\sigma_a\propto1/v\propto E^{-1/2}$</p>
<div class="steps">
<div class="step"><span class="eq">$\lambda_a\propto1/\sigma_a\propto\sqrt{E}$</span><span class="lead"></span><span class="say">截面越小行程越长</span></div>
<div class="step"><span class="eq">$\lambda_a=32.6\times\sqrt{0.001/0.0253}$</span><span class="lead"></span><span class="say">按 $\sqrt{E}$ 缩放</span></div>
<div class="step ind"><span class="eq">$\sqrt{0.001/0.0253}=0.199$</span><span class="lead"></span><span class="say">先把根号算出来</span></div>
<div class="step ind"><span class="eq">$\lambda_a=32.6\times0.199=6.5$ m</span><span class="lead"></span><span class="say">0.001 eV 时的行程</span></div>
<div class="step"><span class="eq">$\lambda_a=32.6\times\sqrt{1/0.0253}$</span><span class="lead"></span><span class="say">1 eV 同样缩放</span></div>
<div class="step ind"><span class="eq">$\sqrt{1/0.0253}=6.29$</span><span class="lead"></span><span class="say">先把根号算出来</span></div>
<div class="step ind"><span class="eq">$\lambda_a=32.6\times6.29=205$ m</span><span class="lead"></span><span class="say">1 eV 时的行程</span></div>
</div>
<p class="a"><span class="lab">答</span>0.001 eV 时 6.5 m，1 eV 时 205 m。能量降到二十五分之一，行程缩到五分之一——中子越慢，在核旁边待得越久，被抓住的机会越大。这里要留一句：0.001 eV 已接近石墨化学键的能量，$1/v$ 律开始失真，实测截面比外推的小，$\lambda_a$ 会比 6.5 m 长一些。</p>
</div>
