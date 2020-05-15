import sys
import json
import os
import datetime
import random
import fitz

class Path():
    def __init__(self, baseDir=""):
        self.path = {"sep": os.sep}
        self.set_path_root()
        baseDir and self.set_path_base(baseDir)
    def set_path_root(self):
        pathArr = os.path.abspath(sys.argv[0]).split(self.path["sep"])
        self.path["enter"] = pathArr.pop()
        self.path["root"] = "{}{}".format(self.path["sep"].join(pathArr), self.path["sep"])

    def set_path_base(self, dir):
        self.set_path("base", dir)

    def set_path_json(self, dir):
        self.set_path("json", dir, self.path["base"])

    def set_path(self, name, dir, root=""):
        path = self.path
        root = root or path["root"]
        self.path[name] = "{1}{2}{0}".format(path["sep"], root, dir)

class File():
    def __init__(self, baseDir):
        self.base = Path(baseDir).path["base"]

    def read(self, fileName):
        if not fileName:
            return False
        url = os.path.join(self.base, fileName)
        self.url = url
        with open(url, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith(u'\ufeff'):
                content = content.encode('utf8')[3:].decode('utf8')
            self.result = json.loads(content)
            return self.result
    def _wr(self, url=""):
        url = self.url if not url == "" else url
        if not self.result:
            return False
        print("开始写入文件", url)
        with open(url, "w", encoding='utf-8') as f:
            json.dump(self.result, f, indent=4, ensure_ascii=False)

    def edit(self):
        if not self.result:
            return False
        self._wr(self.result)

    def write(self, fileName=""):
        if (not fileName):
            return False
        url = os.path.join(self.base, fileName)
        self._wr(url)

    def named(self, type):
        type = type if type.startswith(".") else "."+ type
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 999)) + type

    def up(self, request, input_name, dir="", size=0):
        if input_name in request.files:
            file = ""
            try:
                fi = request.files[input_name]
                filename = fi.filename
                if filename == '':
                    return False
                ftype = '.' + filename.rsplit('.', 1)[1]
                file = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 999)) + ftype
                file_path = os.path.join(self.base, dir, file)
                print(file_path)
                fi.save(file_path)
                fsize = os.stat(file_path).st_size
                if fsize > size * 1024 * 1024 and size != 0:
                    os.remove(file_path)
                    return ""

            except Exception as err:
                print(err)
                pass
            return file
        else:
            return ""

    def up_img(self, request, input_name, dir, size=0, imgs=set(['png', 'jpg', "jpeg"])):
        filename = request.files[input_name].filename
        allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in imgs
        return self.up(request, input_name, dir, size) if allowed else False

    def pdf2img(self, fileName, src_dir, store_dir=""):
        doc = fitz.open(os.path.join(self.base, src_dir, fileName))  # 打开一个PDF文件，doc为Document类型，是一个包含每一页PDF文件的列表
        if not doc.isPDF:
            return False
        store_dir = src_dir if not store_dir else store_dir
        fileName = fileName.split(".")[0]
        target = os.path.join(self.base, store_dir, fileName)

        trans = fitz.Matrix(1, 1).preRotate(0)
        pm = doc[0].getPixmap(matrix=trans, alpha=False)
        tarHeight = 1080
        tarWidth = pm.width / pm.height * tarHeight
        zoom_x = tarWidth / pm.width
        zoom_y = tarHeight / pm.height
        # print("pm>..", pm.width, pm.height,tarWidth,tarHeight,zoom_x,zoom_y)

        rotate = int(0)  # 设置图片的旋转角度
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        # zoom_x = 1.33333333  # 设置图片相对于PDF文件在X轴上的缩放比例(1.33333333-->1056x816)   (2-->1584x1224)
        # zoom_y = 1.33333333  # 设置图片相对于PDF文件在Y轴上的缩放比例
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)  # 缩放系数1.3在每个维度  .preRotate(rotate)是执行一个旋转
        fileNames = []
        print("%s开始转换..." % src_dir)
        if doc.pageCount > 1:  # 获取PDF的页数
            for pg in range(doc.pageCount):
                page = doc[pg]  # 获得第pg页
                pm = page.getPixmap(matrix=trans, alpha=False)  # 将其转化为光栅文件（位数）
                str_path = "%s%s.png" % (target, pg)  # 保证输出的文件名不变
                pm.writeImage(str_path)  # 将其输入为相应的图片格式，可以为位图，也可以为矢量图
                fileNames.append("%s%s.png" % (fileName, pg))
                # 我本来想输出为jpg文件，但是在网页中都是png格式（即调用writePNG），再转换成别的图像文件前，最好查一下是否支持
        else:
            page = doc[0]
            pm = page.getPixmap(matrix=trans, alpha=False)
            pm.writeImage("%s.png" % target)
            fileNames.append("%s.png" % fileName)
        print("转换至%s完成！" % store_dir)
        return fileNames

    def remove(self, dir, fileName):
        path = os.path.join(self.base, dir, fileName)
        os.path.exists(path) and os.remove(path)

    def removes(self, dir, arrs):
        for fileName in arrs:
            self.removeImg(dir, fileName)
