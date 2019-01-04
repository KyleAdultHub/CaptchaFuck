ModelConfig = {
    "test": {
        'epochs': 1,  # 只对生成数据的时候有作用, 生成多少epoch的数据
        'npi': 5,   # 一张图片的元素数量
        'learn_ratio': 0.0001,  # 学习率
        'width': 40 + 20 * 5,  # 图片的宽
        'height': 100,   # 图片的高
        "choice": ["digit", "lower", "upper"],  # 图片的选择集合
        "name": "test",  # 该配置名称
        "keep_prob": 1.0,  # prob参数
        "max_steps": 50000    # 训练到多少步保存并停止
    },
    "wenshu": {
        'npi': 5,  # 一张图片的元素数量
        'learn_ratio': 0.00001,  # 学习率
        'width': 75,  # 图片的宽
        'height': 30,  # 图片的高
        "choice": ["digit", "lower"],  # 图片的选择集合
        "name": "wenshu",  # 该配置名称
        "keep_prob": 1.0,  # prob参数
        "max_steps": 200000,  # 训练到多少步保存并停止
        "conv_num": 3
    },
    "wenshu_upgrade": {
        'npi': 5,  # 一张图片的元素数量
        'learn_ratio': 0.00001,  # 学习率
        'width': 75,  # 图片的宽
        'height': 30,  # 图片的高
        "choice": ["digit", "lower"],  # 图片的选择集合
        "name": "wenshu_upgrade",  # 该配置名称
        "keep_prob": 1.0,  # prob参数
        "max_steps": 120000,  # 训练到多少步保存并停止
        "conv_num": 3
    }
}
