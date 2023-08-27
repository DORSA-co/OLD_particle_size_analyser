import cv2
import numpy as np
import pandas as pd



class detect_test():
    def __init__(self):
        self.debug = False
        self.debug_scale = 0.6
        self.n_objects = 0
        self.px_value=1
    def detect(self, image): 
        # rgb to gray
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)>2 else image
        # if self.debug:
        #     cv2.imshow('Gray Image', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
        #     cv2.waitKey(0)

        # histogram equalization
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(27, 27))
        # gray = clahe.apply(gray)
        # if self.debug:
            # cv2.imshow('Histogram Equalization', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
            # cv2.waitKey(0)

        # bulr image
        gray = cv2.blur(gray,(3,3)) #(self.algo_parasm_obj.blur_ksize, self.algo_parasm_obj.blur_ksize))
        gray = cv2.blur(gray,(7,7))
        gray = cv2.blur(gray,(3,3))
        # gray = cv2.blur(gray, (15,3))
        if self.debug:
            cv2.imshow('Image Bluring', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
            cv2.waitKey(0)
        kernel = np.ones((5,5),np.uint8)
        gray = cv2.erode(gray,kernel,iterations=2)
        # gray threshold
        _, objects_mask = cv2.threshold(gray, 79, 255, cv2.THRESH_BINARY)
        if self.debug:
            cv2.imshow('Objects Mask', cv2.resize(objects_mask, None, fx=self.debug_scale, fy=self.debug_scale))
            cv2.waitKey(0)

        # find contours
        contours, _ = cv2.findContours(objects_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
        # if self.debug:
            # cv2.imshow('Object Contours', cv2.resize(draw_contours_on_image(image=gray, cnts=contours), None, fx=self.debug_scale, fy=self.debug_scale))
            # cv2.waitKey(0)

        # grading
        for cnt in contours:
            # get contour cordinates
            (x1,y1), r = cv2.minEnclosingCircle(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            # get r
            radius = min(w, h, r)
            df1 = pd.read_csv('params.csv', index_col=0)#'params')
            d = df1.values
            # print(float(d[0, 0]))
            params = [float(d[0, 0]), float(d[1, 0]), float(d[2, 0])]
            params = [-2.54562423e-06 , 1.67937821e-06 , 8.29244241e-02]
            # print("read calibration file successfully: ", params)
            # params = [-1.41E-05, -2.93E-06, 0.18027026]#self.algo_parasm_obj.Calibration_Coefficients
            self.px_value = params[0]*x1 + params[1]*y1 + params[2]
            radius_mm = (radius * self.px_value)*2*(0.890)

            # reject those object that arent circular enoug or have size not in desired range
            if area / (np.pi * radius * radius) < 0.65 or not (2<=radius_mm<30):
                continue

            # update count
            self.n_objects+=1
            # circular acc
            circ_acc = min(w, h) / max(w, h)
            print("circ_acc", round(circ_acc,3))

            w_mm = ((w * self.px_value)*(0.904))/2
            h_mm = ((h * self.px_value)*(0.904))/2
            volume1 = (4/3*3.14159*(w_mm*h_mm*h_mm))/1000
            volume2 = (4/3*3.14159*(w_mm*w_mm*h_mm))/1000
            print("w : ",w_mm)
            print("h : ",h_mm)
            max_vol = max(volume1,volume2)
            mean_volumes = round((volume1+volume2)/2, 2)
            # max_volumes = max(volume1,volume2)

            # if 0 < circ_acc < 0.2:
            #     self.circ_acc_array[0]+=1
            # elif 0.2 <= circ_acc < 0.4:
            #     self.circ_acc_array[1]+=1
            # elif 0.4 <= circ_acc < 0.6:
            #     self.circ_acc_array[2]+=1
            # elif 0.6 <= circ_acc < 0.8:
            #     self.circ_acc_array[3]+=1
            # else:
            #     self.circ_acc_array[4]+=1

            # self.circle_acc.append(circ_acc)
            # print(x1 , y1)
            # font = cv2.FONT_HERSHEY_SIMPLEX

           
            # grading
            # for key in self.algo_parasm_obj.ranges_dict.keys():
                # print("radius_mm : ",radius_mm)
            if 2 <= radius_mm < 30:
                # draw contour on image
                cv2.drawContours(image, [cnt], -1, (0, 0, 255), 2)#ImageColor.getcolor(self.algo_parasm_obj.ranges_colors[key], 'RGB'), 2)
                cv2.putText(image, str(mean_volumes) , (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
                
                print("volume of cuntour : ",mean_volumes)
                print("max volume : ",max_vol)
                print("radius_mm : " , round(radius_mm,3))
                    
                    # add tp grading arr
                    # self.grading_ranges_arr[key]+=1
                    
        # if  self.circ_acc_array.sum()!=0:
        #     self.circ_acc_array = (self.circ_acc_array / self.circ_acc_array.sum()) * 100

        # get ranges percentages
        # if  self.grading_ranges_arr.sum() != 0:
        #     self.grading_ranges_arr = self.grading_ranges_arr / self.grading_ranges_arr.sum() * 100
        
        # if self.debug:
        cv2.imshow('Grading Results', cv2.resize(image, None, fx=0.4, fy=0.4))
        cv2.waitKey(0)

        # with open('Grading_Resualt.csv', 'w') as csvfile:
        #     writer=csv.writer(csvfile, delimiter=',')
        #     writer.writerows(zip((self.grading_ranges_arr / self.grading_ranges_arr.sum()) * 100, np.array(self.circle_acc).mean() * 100 , self.n_objects))

        # print("self.grading_ranges_arr " , self.grading_ranges_arr)
        # print("np.array(self.circle_acc).mean() : ",np.array(self.circle_acc).mean())
        # print("self.circ_acc_array :",self.circ_acc_array)
        print(self.n_objects)
        return image#, (self.grading_ranges_arr / self.grading_ranges_arr.sum()) * 100, self.circ_acc_array, self.n_objects

if __name__=='__main__':
    path = 'C:/Users/Dorsa-PC/Desktop/new_cal/test/new5'
    Grad_test = detect_test()
    import os
    for fname in os.listdir(path):
    # for i in range(100):
        image = cv2.imread(os.path.join( path, fname))# + "Basler_acA1920-40gm__23685575__20221212_160152744_0000.tiff")#os.path.join( path, fname))  
        img = Grad_test.detect(image)
        cv2.imwrite(path+"test"+str(fname.index)+".tiff", img)
        # cv2.imshow('Smart Laboratory Grading System ',cv2.resize(image_res,None, fx=0.3,fy=0.3))
        # cv2.waitKey(50)