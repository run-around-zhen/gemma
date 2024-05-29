import matplotlib.pyplot as plt
import matplotlib
 
# 设置字体
title_zhfont = matplotlib.font_manager.FontProperties(
    fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    size=15
)
axis_zhfont = matplotlib.font_manager.FontProperties(
    fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    size=10
)
 
# 创建数据
x = [1, 2, 3, 4, 5]
y = [1, 4, 2, 3, 5]
 
# 创建折线图
plt.plot(x, y)
 
# 添加标题和坐标轴标签
plt.title('我的折线图', fontproperties=title_zhfont)
plt.xlabel('x轴', fontproperties=axis_zhfont)
plt.ylabel('y轴', fontproperties=axis_zhfont)
 
# 显示图形
plt.show()