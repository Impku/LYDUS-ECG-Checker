

# images processing
import cv2
# matrix processing
import numpy as np
# others
import sys

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pandas as pd
import ecg_plot
import cv2
from ast import literal_eval
import base64
import array
import imutils
from PIL import ImageQt,Image

import logging
import os
import time

date_strftime_format = "%d-%b-%y %H:%M:%S"
message_format = "[%(asctime)s]  %(message)s"
logging.basicConfig(level=logging.INFO, format=message_format, datefmt=date_strftime_format, encoding='utf-8')

keydict = {"0018|1111":"Distance Source to Patient","0018|1147":"Field of View Shape","0018|1149":"Field of View Dimensions","0028|0030":"Pixel Spacing","0028|0106":"Smallest Image Pixel Value","0028|0107":"Largest Image Pixel Value","0028|0A02":"Pixel Spacing Calibration Type","0028|1052":"Rescale Intercept","0028|1053":"Rescale Slope","0028|1054":"Rescale Type","0008|002A":"Acquisition DateTime","0008|0060":"Modality","0008|0070":"Manufacturer","0008|1030":"Study Description","0008|103E":"Series Description","0010|0020":"Patient ID","0010|0040":"Patient's Sex","0010|1010":"Patient's Age","0018|0015":"Body Part Examined","0018|1000":"Device Serial Number","0018|1050":"Spatial Resolution","0018|1164":"Imager Pixel Spacing","0018|5101":"View Position","0020|0060":"Laterality","0028|0004":"Photometric Interpretation","0028|0010":"Rows","0028|0011":"Columns","0028|0034":"Pixel Aspect Ratio"}

class thread(QThread):
    log = pyqtSignal(str)

    def __init__(self, df, parent=None):
        QThread.__init__(self, parent)
        self.df = df

    def run(self) -> None:
        time.sleep(.5)

        class1 = ["AlsUnitNo","Examdt","VentricularRate","PRInterval","QRSDuration","QTInterval","QTCorrected","PAxis","RAxis","TAxis","Diagnosis","RestingECG.Diagnosis.DiagnosisStatement"]
        class2 = ["WaveformType","WaveformStartTime","NumberofLeads","SampleType","SampleBase","SampleExponent","HighPassFilter","LowPassFilter","ACFilter"]
        class3 = ["LeadByteCountTotal","LeadTimeOffset","LeadSampleCountTotal","LeadAmplitudeUnitsPerBit","LeadAmplitudeUnits","LeadHighLimit","LeadLowLimit","LeadID","LeadOffsetFirstSample","FirstSampleBaseline","LeadSampleSize","LeadOff","BaselineSway","LeadDataCRC32"]
        #,"WaveFormData"
        # try:

        waveform = literal_eval(self.df['Waveform'][0])[1]
        lead_data = waveform['LeadData'][0]

        truth = 0
        false = 0

        self.log.emit(f" Check First Class Attributes")

        for c in class1:
            if c in self.df.columns and self.df[c][0] != None and str(self.df[c][0])!= "nan":
                data = self.df[c][0]
                # self.logTextBox.texteditor.append(metadata+f"({keydict[metadata]}) " + data)
                # logging.info(f"{keydict[metadata]}.....True")
                self.log.emit(f"{c}.....True_{data}")
                truth += 1
            else:
                # self.logTextBox.texteditor.append(metadata+f"({keydict[metadata]})")
                # logging.info(f"{keydict[metadata]}.....False")
                self.log.emit(f"{c}.....False")
                # self.logTextBox.texteditor.setHtml("<font color='red' size='6'><red>Hello PyQt5!\nHello</font>")
                false += 1
            time.sleep(.1)

        self.log.emit(f" Check Second Class Attributes")
        for c in class2:
            if c in list(waveform.keys()) and waveform[c] != None and str(waveform[c]) != "nan":
                print(data)
                data = waveform[c]
                # self.logTextBox.texteditor.append(metadata+f"({keydict[metadata]}) " + data)
                # logging.info(f"{keydict[metadata]}.....True")
                self.log.emit(f"{c}.....True_{data}")
                truth += 1
            else:
                # self.logTextBox.texteditor.append(metadata+f"({keydict[metadata]})")
                # logging.info(f"{keydict[metadata]}.....False")
                self.log.emit(f"{c}.....False")
                # self.logTextBox.texteditor.setHtml("<font color='red' size='6'><red>Hello PyQt5!\nHello</font>")
                false += 1
            time.sleep(.1)

        self.log.emit(f" Check Third Class Attributes")
        for c in class3:
            if c in list(lead_data.keys()) and lead_data[c] != None and str(lead_data[c]) != "nan":
                data = lead_data[c]
                # self.logTextBox.texteditor.append(metadata+f"({keydict[metadata]}) " + data)
                # logging.info(f"{keydict[metadata]}.....True")
                self.log.emit(f"{c}.....True_{data}")
                truth += 1
            else:
                # self.logTextBox.texteditor.append(metadata+f"({keydict[metadata]})")
                # logging.info(f"{keydict[metadata]}.....False")
                self.log.emit(f"{c}.....False")
                # self.logTextBox.texteditor.setHtml("<font color='red' size='6'><red>Hello PyQt5!\nHello</font>")
                false += 1
            time.sleep(.1)


        self.log.emit(f"**Done**_{truth}_{false}")


class QTextEditLogger(logging.Handler):

    def __init__(self, parent):
        super().__init__()
        self.texteditor = QTextEdit(parent)
        self.texteditor.setFixedWidth(400)
        self.texteditor.setReadOnly(True)
        self.texteditor.setPlainText("Welcome to ECG Checker!\n")


    def emit(self, record):
        msg = self.format(record)
        self.texteditor.append(msg)
        self.texteditor.ensureCursorVisible()
        self.texteditor.viewport().update()

class MyApp(QWidget):
    sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.item_dict = dict()
        self.missingItem = []

        self.initUI()

    def initUI(self):
        ack_txt = " \n\nECG Checker\n\n version: 1.0.0 (update: November 11, 2022)\n\n- This program is used to estimate your ECG file and give a score based on the most\n  important 21 features in ECG header. Data type and data range will be considered\n in the test. \n - If a score of ECG file is lower then 90, this ECG file may cause \n trouble to your research.\n\n This program made by Yonsei Boncentricq Team\n\n\n Funding:\n\n a grant of the Korea Health Technology R&D Project through the Korea Health Industry\n Development Institute (KHIDI), funded by the Ministry of Health & Welfare, \n Republic of Korea (HI22C0452)"
        self.lbl_img = QLabel(ack_txt)
        self.lbl_img.setAlignment(Qt.AlignLeft)

        self.upload_btn = QPushButton("Load a csv / tsv file",self)
        self.upload_btn.clicked.connect(self.btn_fun_FileLoad)

        self.analyze_btn = QPushButton("Analyze",self)
        self.analyze_btn.clicked.connect(self.btn_fun_Analyze)
        self.analyze_btn.setEnabled(False)

        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(logging.Formatter(message_format,"%Y-%m-%d %H:%M:%S"))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.INFO)

        # self.ui.sub_widget = SubWidget()

        vbox = QGridLayout()
        vbox.addWidget(self.lbl_img,0,0)
        vbox.addWidget(self.upload_btn,2,0)
        vbox.addWidget(self.logTextBox.texteditor,0,1,2,1)
        vbox.addWidget(self.analyze_btn,2,1)
        self.setLayout(vbox)


        self.setFixedSize(1000, 600)
        self.setMouseTracking(False)
        self.setWindowTitle('EKG Checker - Bonecentricq')
        self.move(300, 300)

        self.show()

    # thread log 처리기
    @pyqtSlot(str)
    def appendLog(self, string):
        if "**Done**" not in string:
            if "....True" in string:
                self.item_dict[string.split(".....")[0]] = string.split("True_")[1]
                self.logTextBox.texteditor.append(" - "+string.split("True_")[0]+"True")
                self.logTextBox.texteditor.viewport().update()

            elif "....False" in string:
                self.missingItem.append(string.split(".....")[0])
                self.logTextBox.texteditor.append(" - "+string)
                self.logTextBox.texteditor.viewport().update()

            else:
                self.logTextBox.texteditor.append(" * "+string)
                self.logTextBox.texteditor.viewport().update()


        else:
            truth = float(string.split("_")[1])
            false = int(string.split("_")[-1])

            self.show_popup(truth,false)

            # self.logTextBox.texteditor.append(str(truth/21))
            self.logTextBox.texteditor.append(f"\n ** Curation score : {int((truth/(int(truth)+int(false)))*100)} / 100")
            self.logTextBox.texteditor.append(f" ** This ECG file has {false} missing values\n")

            self.logTextBox.texteditor.append("\n".join([ " - "+i+": -" for i in self.missingItem])+"\n")
            self.logTextBox.texteditor.viewport().update()
            
            logging.info('Success to analyze ECG metadatas')
            self.logTextBox.texteditor.viewport().update()

            self.upload_btn.setEnabled(True)
            self.analyze_btn.setEnabled(False)

    def show_popup(self,truth,false):
        msg = QMessageBox()
        msg.setWindowTitle("ECG analysis results")
        msg.setText(f"- Analysis reports\n Curation score : {int((truth/(int(truth)+int(false)))*100)} / 100\n This ECG file has {false} missing values")
        msg.setIcon(QMessageBox.Information)
        txt = "* Missing value\n" +"\n".join([ " - "+i+": -" for i in self.missingItem])
        txt += "\n" + "="*20 + "\n"
        txt += "\n".join([f" - {key}:{value}" for key, value in self.item_dict.items()])
        msg.setDetailedText(txt)
        x = msg.exec_() 

    # extract leaddata
    def extract_leads(self,df):

        lead_data = literal_eval(df['Waveform'][0])[1]['LeadData']
        result_dict = {}

        for x in lead_data: #8 leads in lead_data (len=8)

            waveform = x['WaveFormData']

            laupb = float(x['LeadAmplitudeUnitsPerBit'])

            waveform_decoded = base64.b64decode(waveform)
            waveform_decoded = np.array(array.array('h', waveform_decoded))
            # waveform_decoded = (waveform_decoded*laupb).astype(int)
            waveform_decoded = (waveform_decoded*laupb) / 1000
            result_dict[x['LeadID']] = waveform_decoded

        # result_dict['III'] = np.subtract(result_dict['II'], result_dict['I']).astype(int)
        # result_dict['aVR'] = (np.add(result_dict['I'], result_dict['II'])*(-0.5)).astype(int)
        # result_dict['aVL'] = np.subtract(result_dict['I'], 0.5*result_dict['II']).astype(int)
        # result_dict['aVF'] = np.subtract(result_dict['II'], 0.5*result_dict['I']).astype(int)

        result_dict['III'] = np.subtract(result_dict['II'], result_dict['I'])
        result_dict['aVR'] = (np.add(result_dict['I'], result_dict['II'])*(-0.5))
        result_dict['aVL'] = np.subtract(result_dict['I'], 0.5*result_dict['II'])
        result_dict['aVF'] = np.subtract(result_dict['II'], 0.5*result_dict['I'])

        lead12_df = pd.DataFrame.from_dict(result_dict)

        return lead12_df

    # upload file
    def btn_fun_FileLoad(self):        
        fname=QFileDialog.getOpenFileName(self,filter="TSV file(*.tsv)")

        logging.info(f'Start to upload a EKG raw data : {os.path.basename(fname[0])}')

        # try:
        self.ekgname = fname[0]
        # self.loaded_image = cv2.imread(self.ekgname,0)
        self.ekg_df = pd.read_csv(self.ekgname, encoding='cp949', sep='\t')
        self.ekg_lead_df = self.extract_leads(self.ekg_df)
        for col in self.ekg_lead_df.columns:
            self.ekg_lead_df[col] = (self.ekg_lead_df[col] - self.ekg_lead_df[col].mean()) / self.ekg_lead_df[col].std()
        # image = (np.clip(self.loaded_image,0,255)).astype(np.uint8)

        ecg_plot.plot_12(self.ekg_lead_df.T.values, sample_rate = 500,lead_index =self.ekg_lead_df.columns,columns=1,title="")
        ecg_plot.save_as_png('example_ecg','tmp/')

        image = Image.open("tmp/example_ecg.png")
        image = image.resize((400,424))
        image = ImageQt.ImageQt(image)
        pixmap = QPixmap.fromImage(image).scaledToWidth(500) 
        self.lbl_img.setPixmap(pixmap)

        logging.info(f'Success to upload a EKG rawdata : {os.path.basename(fname[0])}')

        self.upload_btn.setEnabled(False)
        self.analyze_btn.setEnabled(True)

        # except:
        #     logging.info(f'Fail to load a EKG text file : {os.path.basename(fname[0])}')
        #     logging.info(f'Please check your EKG file')


    # Analyzer
    def btn_fun_Analyze(self):        

        logging.info(f'Start to analyze EKG metadatas')
        
        # inactive btn
        self.analyze_btn.setEnabled(False)
        
        # start thread
        self.thread_str = thread(self.ekg_df)
        self.thread_str.start()
        self.thread_str.log.connect(self.appendLog)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())