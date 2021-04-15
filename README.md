# pdf2audio
transform pdf document to audio to achieve the goal "learning in sleeping"

最近看到一个[文章](https://mp.weixin.qq.com/s/BZ3iEaTyYaHdt62zdyPflQ)，表明边睡边学真的可行，只要睡觉的时候听一些学过的东西，就能躺着刷技能熟练度，于是我寻思着把论文转成音频，晚上睡觉的时候听，既能催眠又能啥都不干躺着刷熟练度。这里记录下如何实现。

本文主要使用Python3来实现，简单易上手，代码全部[开源](https://github.com/you8023/pdf2audio)，让大家也可以跟我一起007（bushi）

**如果本文图片无法加载，请到[博客](https://www.jianshu.com/p/01e0343bb082)查看详情**

**如果不想了解技术细节，只想直接拿来用，可以直接跳过代码编写部分，直达最后代码使用部分。如果你觉得好用，希望能够给我一个赞（能打赏更好），也欢迎去[github](https://github.com/you8023/pdf2audio/issues)发表意见建议。**

## 开发环境
* Windows 10
* Sublime Text 3
* 谷歌gTTS模块
* pdfminer

## 准备
在网上搜了下，没有现成的pdf转mp3的方法，于是大致思路为：

1. pdf文字提取
2. 文字转音频

以此实现pdf转MP3

这里使用`pdfminer`实现文字提取，首先安装依赖：
```
pip install pdfminer4k
```

此外，还需要安装谷歌`gTTS`模块：
```
pip install gTTS
```
## 代码编写
### pdf文字提取
编写代码（注意要对提取的文字做处理，不然结果会比较杂乱）：
```python
def pdfread(pdfPath):
	with open(pdfPath, 'rb') as fp:
		try:

			print(pdfPath)
			#用文件对象创建一个PDF文档分析器
			parser = PDFParser(fp)
			#创建一个PDF文档
			doc = PDFDocument()
			#分析器和文档相互连接
			parser.set_document(doc)
			doc.set_parser(parser)
			#提供初始化密码，没有默认为空
			doc.initialize()
			#检查文档是否可以转成TXT，如果不可以就忽略
			if not doc.is_extractable:
				raise PDFTextExtractionNotAllowed
			else:
				#创建PDF资源管理器，来管理共享资源
				rsrcmagr = PDFResourceManager()
				#创建一个PDF设备对象
				laparams = LAParams()
				#将资源管理器和设备对象聚合
				device = PDFPageAggregator(rsrcmagr, laparams=laparams)
				#创建一个PDF解释器对象
				interpreter = PDFPageInterpreter(rsrcmagr, device)
				allContent = ''
				last_para = ''
				result = ''
				for page in doc.get_pages():
					interpreter.process_page(page)
					#接收该页面的LTPage对象
					layout = device.get_result()
					#这里的layout是一个LTPage对象 里面存放着page解析出来的各种对象
					#一般包括LTTextBox，LTFigure，LTImage，LTTextBoxHorizontal等等一些对像
					#想要获取文本就得获取对象的text属性
					
					for x in layout:
						try:
							if(isinstance(x, LTTextBoxHorizontal)):
								result = x.get_text()
								# 去掉pdf文件读取的各种换行符
								result = result.replace('\n', '')
								# 去掉参考文献引用
								result = re.sub('\[(\d+\,* ?-?)+\]', '', result)
								# 无序列表换行
								result = result.replace('∙', '\n∙')
								# 去掉参考文献
								if re.findall('^references?', last_para.lower().replace(' ', '')) != [] or re.findall('^references?', result.lower().replace(' ', '')) != []:
									return allContent
								# 去掉页脚页码页眉以及内容过少的表格
								if re.findall('^Authorized licensed use limited to:', result) == [] and re.findall('©', result) == [] and re.findall('Publication date', result) == [] and re.findall('\d\:\d', result) == [] and re.findall('(et al.)$', result) == [] and len(result) > 5:
									allContent = allContent + '\n' + result
								# print(result)
						except Exception as e:
							print(e)
						last_para = result
				return allContent
		except Exception as e:
			print('文档读取失败：' + str(e))
```
### 文字转音频
编写代码，这里的参数`lang`表示文字语言，`text`即为要转化的文字：
```python
tts = gTTS(text=result, lang='en')
tts.save("test.mp3")
```
### 主函数
主函数最终为：
```python
if __name__ == '__main__':

	pdfPath = 'a37-islam.pdf' # 需要转换的同一目录下的文件名
	result = pdfread(pdfPath)
	print(result)

	tts = gTTS(text=result, lang='en')
	tts.save("test.mp3")
```

## 使用
首先先[下载代码](https://github.com/you8023/pdf2audio)

然后修改代码中的主函数内的 `pdfPath`参数为自己想要转换的pdf文档的路径，然后直接在控制台内使用命令运行程序：
```
python pdf2audio.py
```
然后静静等候，等程序运行完毕，就能看到和代码同级目录下出现了一个`test.mp3`，即为生成的音频：
![代码运行](https://upload-images.jianshu.io/upload_images/5714082-54d5f437f493488e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![生成的音频](https://upload-images.jianshu.io/upload_images/5714082-8490b2f2e7d636f2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**注意：**
1. 程序运行过程中不能断网
2. 程序运行时间较长（出bug会直接报错，程序没有写死循环，请放心食用），请耐心等候
3. 论文越长，程序运行时间越久，生成的音频也越大
