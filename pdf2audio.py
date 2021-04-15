from gtts import gTTS
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from io import StringIO
import re

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

if __name__ == '__main__':

	pdfPath = 'a37-islam.pdf' # 需要转换的同一目录下的文件名
	result = pdfread(pdfPath)
	print(result)

	tts = gTTS(text=result, lang='en')
	tts.save("test.mp3")