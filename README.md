# 实验配置
参考https://github.com/conweave-project/conweave-ns3 中Run NS-3 on Ubuntu 20.04进行配置即可，基本使用在该文档中均可见到。

# 实验图复现
实验数据从云盘下载https://cloud.189.cn/t/3A3muiJNzANn （访问码：6jo5）

将指定的数据复制到mix/output目录下，同时复制.history中的内容

运行analysis/plot_xxx.py画图文件即可

# 代码运行
在run.py中修改如下的地方，修改负载均衡算法、网络负载、网络拓扑，运行后即可生成数据文件
![cdc43310bfb9078440ec4cdcd660ec1](https://github.com/run-around-zhen/gemma/assets/55088145/da984f8b-1301-4c9c-a2a2-c416a1afcd25)
运行画图文件即可

**一些备注：**
以下文件均在src/point-to-point/model文件夹下

只添加了两个文件：
gemma.h/cc:gemma的具体实现，其余的均无改动

动态负载的修改，gemma.cc中把10修改为responseNum即可
![f45921f5b505cb80f30d3989e081e3d](https://github.com/run-around-zhen/gemma/assets/55088145/705011fd-a351-49a5-a423-6b2a4a825806)

Incast的修改，在run.py中调用Incast.py后缀的文件，生成Incast流文件
![56bd4dcc3924578e3de5b4237b18d3e](https://github.com/run-around-zhen/gemma/assets/55088145/c73de0d8-8501-402e-8ce7-b3aa0bfe6327)
