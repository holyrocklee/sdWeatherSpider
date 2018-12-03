# -*- coding: utf-8 -*-
from re import findall
from urllib.request import urlopen
import scrapy
from sdWeatherSpider.items import SdweatherspiderItem


class EverycityinsdPySpider(scrapy.Spider):
    name = 'everyCityinSD'
    allowed_domains = ['www.weather.com.cn']
    start_urls = []
    #遍历各城市，获取要爬取的页面URL
    url = r'http://www.weather.com.cn/shandong/index.shtml'
    # 文件使用完毕后必须关闭，因为文件对象会占用操作系统的资源，并且操作系统同一时间能打开的文件数量也是有限的
    # 每一次读写文件后都要写一个fp.close()实在太繁琐，所以，Python引入了with语句来自动帮我们调用close()方法
    with urlopen(url) as fp:
        contents = fp.read().decode()
        # 上面是把山东天气预报的整个首页的html源码给爬下来了，发现其中还包括类似于东北、华南各城市的城市
        # 推断只有第一个得到的才是山东各城市相关源码，即url[0]，print(contents)
    pattern = '<a title=".*?" href="(.+?)" target="_blank">(.+?)</a>'
    # 首页17个城市的正则匹配
    for url in findall(pattern,contents):
        # print(url), 分析用
        start_urls.append(url[0])

    def parse(self, response):
        # 处理每个城市的天气预报页面数据，XML文档：XPath 使用路径表达式在 XML 文档中选取节点。
        # 节点是通过沿着路径或者 step 来选取的。
        item = SdweatherspiderItem()
        # //div[@class="crumbs fl"]选取所有 div 元素，且这些元素拥有值为 crumbs f1 的 class 属性。
        city = response.xpath('//div[@class="crumbs fl"]//a[2]//text()').extract()[0]
        item['city'] = city

        #每个页面只有一个城市的天气数据，直接取[0]
        selector = response.xpath('//ul[@class="t clearfix"]')[0]

        # 存放天气数据
        weather = ''
        for li in selector.xpath('./li'):
            date = li.xpath('./h1//text()').extract()[0]
            cloud = li.xpath('./p[@title]//text()').extract()[0]
            high = li.xpath('./p[@class="tem"]//span//text()').extract()[0]
            #今日天气有时只显示当前温度，不会会显示最高和最低，，待改进,extract()经常使用来切片（脱壳）从一个对象中得到list
            low = li.xpath('./p[@class="tem"]//i//text()').extract()[0]
            # 此处风向不准确，有南风转北风
            wind = li.xpath('./p[@class="win"]//em//span[1]/@title').extract()[0]
            wind = wind+li.xpath('./p[@class="win"]//i//text()').extract()[0]

            weather = weather + date+':'+cloud+','+high+r'/'+low+','+wind+'\n'
        item['weather'] = weather
        return [item]

