from matplotlib import backends
import numpy as np
import cv2
from scipy.spatial import distance



def draw_contour(gray, cnts):
    """
    this function is used to draw nput contours on image

    Args:
        gray (_type_): image in gray format
        cnts (_type_): contours

    Returns:
        image: image with drawed contours
    """
    print("draw contour func")
    img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    img = cv2.drawContours( img, cnts , -1, (0,0,255), thickness=8)
    return img


def draw_rect(gray, cnts, areas):
    """
    this function is used to draw input recangle contours on image

    Args:
        gray (_type_): image in gray format
        cnts (_type_): contours
        areas (_type_): list of areas of rectangles (in mm)

    Returns:
        image: image with drawed contours
    """
    print("draw rect func")
    img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    print("# of contours",len(cnts))
    for i,cnt in enumerate(cnts):
        x,y,w,h = cv2.boundingRect(cnt)
        color = (np.random.randint(0,255),np.random.randint(0,255),np.random.randint(0,255),)
        cv2.putText( img, str(areas[i]) , (x,y) , cv2.FONT_HERSHEY_DUPLEX, 1, color )
        img = cv2.drawContours( img, [cnt] , 0, color, thickness=3)

    return img



class extract_info():
    """
    this class is used to get pixel-value of camera, using the Dorsa calibrator plate with 6 rectangles (3 pairs)

    Args:
        gray: input image in gray format
        areas_mm: list of areas of rectangles (in mm), containing 6 area value, first 3 for large rects, and last 3 for small rects
        min_area: min area of contours (in pixel)
        max_area: max area of contours (in pixel)
        accuracy: min rectangular accuracy for contours
        gray_thrs: gray threshhold for thresholding
    
    Returns:
        None
    """

    def __init__(self, gray, areas_mm , min_area=2000, max_area=50000 , accuracy=0.9, gray_thrs=100):
        self.nrects = len(areas_mm)
        self.areas_mm = list(areas_mm)
        self.gray = np.array(gray, dtype=np.uint8)
        self.min_area = min_area
        self.max_area = max_area
        self.accuracy = accuracy
        self.gray_thrs = gray_thrs
        print("extract info class")
    
    def thrs_map(self):
        """
        get thresholded/mask from input image

        Args: None

        Returns:
            mask: threshold mask of input image
        """

        _, mask = cv2.threshold(self.gray, self.gray_thrs, 255, cv2.THRESH_BINARY)
        print("thresholding")
        return mask

    
    def find_contours(self, mask):
        """
        find countours of threshold mask

        Args:
            mask (_type_): threshold mask

        Returns:
            img: image with drawed countours
            cnts: foundeed counturs
        """
        print("find contours")
        cnts,_ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        img = draw_contour(self.gray, cnts)
        return img, cnts
        
    
    def filter_contours_by_area(self, cnts):
        """
        this function is used to filter founded contours by min and max area

        Args:
            cnts (_type_): input contours

        Returns:
            img: image with drawed countours
            cnts: area filtered counturs
        """
        print("filter contours by size")
        filter_area = lambda x: self.min_area< cv2.contourArea(x) < self.max_area
        cnts = list( filter( filter_area, cnts))
        print("numbers of contours left after size filter: ", len(cnts))
        img = draw_contour( self.gray, cnts)
        return img, cnts

    
    def filter_acc(self, x):
        """
        this function is used to filter a countour by its accuracy to be rectangular

        Args:
            x (_type_): _description_

        Returns:
            _type_: _description_
        """

        _,(w,h),_ = cv2.minAreaRect(x)
        rect_area = w*h
        area = cv2.contourArea(x)
        print("calculate metric to filter by accurcy")
        return area/rect_area > self.accuracy


    def filter_contours_by_accuracy(self, cnts):
        """
        this function is used to filter countours by their accuracy to be rectangular

        Args:
            cnts (_type_): input contours

        Returns:
            img: image with drawed countours
            cnts: rectangle accuracy filtered counturs
        """

        cnts = list( filter( self.filter_acc, cnts))
        img = draw_contour( self.gray, cnts)
        print("number of contours left after filter by accuracy: ", len(cnts))
        return img, cnts

    
    def draw_rects(self, cnts):
        """
        this function is used to draw rectangular contours on image

        Args:
            cnts (_type_): input contours

        Returns:
            img: image with drawed countours
            rects: list of 6 rectangle countours
        """

        cnts.sort(key = lambda x:cv2.contourArea(x), reverse=True)
        rects = cnts[:self.nrects]
        print("number of rects: ", len(rects))
        self.areas_mm.sort(reverse=True)
        img = draw_rect( self.gray, rects, self.areas_mm)
        # cv2.imshow("img", img)
        # cv2.waitKey(100)
        # print("draw rect")

        return img, rects


    def final_decision(self, cnts, rects):
        """
        this function is used to get pixel-values for each of rrectangle pairs

        Args:
            cnts (_type_): input contours
            rects (_type_): input 6 rectangle contours

        Returns:
            resault: determining if done
            infoes: array of rectangle pair centers and pixel values
            infoes_final: array of rectangle pair centers and pixel values
        """
        print("final decesion")
        print("n of left contours to decide on: ", len(cnts))
        print("n of left rects to decide on: ", len(rects))
        # check if all 6 rects are detected
        if len(cnts) < self.nrects:
            
            return False, 0, 0
        # else
        infoes = []
        for i in range(len(rects)):
            (x,y),_,_ = cv2.minAreaRect(rects[i])
            area_px = cv2.contourArea(rects[i])
            area_mm = self.areas_mm[i]
            px2mm = np.sqrt( area_mm/ area_px )
            infoes.append([x,y , px2mm])
        infoes = np.array(infoes)
        print("size of infoes array: ", len(infoes))
        # sorting contours to assign each small rect to its paired large rect (check by rects centers)
        print("sorting contours to assign each small rect to its paired large rect (check by rects centers)")
        infoes_final = []
        for i in range(len(rects)//2):
            large_rect = (infoes[i,0], infoes[i,1])
            dist_min = np.Infinity
            j_itr = 0
            for j in range(len(rects)//2, len(rects)):
                small_rect = (infoes[j,0], infoes[j,1])
                # check distance
                if distance.euclidean(large_rect, small_rect) <= dist_min:
                    dist_min = distance.euclidean(large_rect, small_rect)
                    j_itr = j
            # append
            infoes_final.append(np.mean(np.array([infoes[i], infoes[j_itr]]), axis=0))
            print("size of final infoes: ", len(infoes_final))
        return True, infoes, np.array(infoes_final)


    def solve_equation( self,inputs):
        """
        this function is used to solve equation for finding pixel value parameters

        Args:
            inputs (_type_): _description_

        Returns:
            pixel_value_parameters: array of 3 parameters
        """

        inputs = np.array(inputs)
        print("size of solve eq inputs",inputs.shape)
        inputs = np.insert(inputs, -1, 1, axis=1)
        # print(inputs)
        d = np.copy( inputs[:,:3] )
        print("d", d)
        dx = np.copy( d )
        dx[:,0] = inputs[:,-1]
        
        dy = np.copy( d )
        dy[:,1] = inputs[:,-1]
        
        dz = np.copy( d )
        dz[:,2] = inputs[:,-1]

        d = np.linalg.det(d)
        dx = np.linalg.det(dx)
        dy = np.linalg.det(dy)
        dz = np.linalg.det(dz)

        kx = dx/d
        ky = dy/d
        kz = dz/d

        return np.array([kx,ky,kz])



# pixel value calibration
def apply_pxvalue_calibration(image, next=True, calib_enable = False, min_area = 250, max_area = 175000, gray_thrs = 127):
    """
    this function is used in pixel value calibration.
    the pixel value calibration is done during some steps,
    in every call of this function, one step (next/prev) is done and the results are updated on ui.
    this way, we can change between steps and tune parameters to get pixel value results

    Inputs:
        ui_obj: main ui object
        api_obj: main api object
        db_obj: database object
        image: input calibration image
        next: a boolean value determninig wheater take to next step or previous step
    
    Returns: None
    """   
    
    step = 0#api_obj.pxcalibration_step # get the current step
    # api_obj.pxcalibration_step = 0

    # disable apply button and soft-calibration params if enable
    # ui_obj.calib_save_params.setEnabled(False)
    # ui_obj.calib_rotate_spinbox.setEnabled(False)
    # ui_obj.calib_shifth_spinbox.setEnabled(False)
    # ui_obj.calib_shiftw_spinbox.setEnabled(False)
    # ui_obj.calib_radio_corsshair.setEnabled(False)
    # ui_obj.calib_radio_grid.setEnabled(False)

    #
    try:
        if image == None:
            print("no image")
            #ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.WARNINGS['camera_no_picture'][ui_obj.language], level=1)
            

    except:
        # select wheather apply or not soft-calibration to image
        # camera_calibration_params = camera_funcs.get_camera_calibration_params_from_ui(ui_obj=ui_obj)
        # image = camera_funcs.apply_soft_calibrate_on_image(ui_obj=ui_obj, image=image, camera_calibration_params=camera_calibration_params, pxcalibration=True)
        
        # apply pxvalue calibration
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # cv2.imshow("img", image)
        # cv2.waitKey(100)
        # get calibration params from database and UI
        # rect_areas, rect_acc = mainsetting_funcs.get_mainsetting_params_from_db(db_obj=db_obj, mode='px_calibration')
        rect_areas = [50,200,50,200,50,200]
        rect_acc = 0.9
        min_area = 250#camera_calibration_params['calib_minarea']
        max_area = 175000#camera_calibration_params['calib_maxarea']
        gray_thrs = 127#camera_calibration_params['calib_thrs']
        # define calibration class
        calibration_obj = extract_info(gray=image, areas_mm=rect_areas, min_area=min_area, max_area=max_area, accuracy=rect_acc, gray_thrs=gray_thrs)
        print(calibration_obj)
    # next
    if next:
        #
        if step >= 0:
            img = calibration_obj.thrs_map()
            if calib_enable : 
                cv2.imshow("calibration_obj", cv2.resize(img, (0, 0), fx = 0.4, fy = 0.4))
                cv2.waitKey(0)
            step += 1
            # api_obj.pxcalibration_step += 1
            # ui_obj.pixelvalue_prev_btn.setEnabled(True)
        #
        if step >= 1:
            img, cnts = calibration_obj.find_contours(img)
            if calib_enable : 
                cv2.imshow("find_contours",cv2.resize(img, (0, 0), fx = 0.4, fy = 0.4))
                cv2.waitKey(0)
            step += 1
            # api_obj.pxcalibration_step += 1
        #
        if step >= 2:
            img, cnts = calibration_obj.filter_contours_by_area(cnts)
            if calib_enable : 
                cv2.imshow("filter_contours_by_area", cv2.resize(img, (0, 0), fx = 0.4, fy = 0.4))
                cv2.waitKey(0)
            step += 1
            # api_obj.pxcalibration_step += 1
        #
        if step >= 3:
            img, cnts = calibration_obj.filter_contours_by_accuracy(cnts)
            if calib_enable : 
                cv2.imshow("filter_contours_by_accuracy", cv2.resize(img, (0, 0), fx = 0.4, fy = 0.4))
                cv2.waitKey(0)
            step += 1
            # api_obj.pxcalibration_step += 1
        #
        if step >= 4:
            img, rects = calibration_obj.draw_rects(cnts)
            step += 1
            # api_obj.pxcalibration_step += 1
        #
        if step >= 5:
            succ, _, infoes = calibration_obj.final_decision(cnts, rects)
            step += 1
            # ui_obj.pixelvalue_next_btn.setEnabled(False)
            # api_obj.pxcalibration_step += 1
    # prev
    if not next:
        #
        if step >= 1:
            img = image
            # ui_obj.pixelvalue_prev_btn.setEnabled(False)
            # api_obj.pxcalibration_step = step - 1
        #
        if step >= 2:
            img = calibration_obj.thrs_map()
            # api_obj.pxcalibration_step = step - 1
            # ui_obj.pixelvalue_prev_btn.setEnabled(True)
        #
        if step >= 3:
            img, cnts = calibration_obj.find_contours(img)
            # api_obj.pxcalibration_step = step - 1
            #
        if step >= 4:
            img, cnts = calibration_obj.filter_contours_by_area(cnts)
            # api_obj.pxcalibration_step = step - 1
        #
        if step >= 5:
            img, cnts = calibration_obj.filter_contours_by_accuracy(cnts)
            # api_obj.pxcalibration_step = step - 1
        #
        if step >= 6:
            img, rects = calibration_obj.draw_rects(cnts)
            # api_obj.pxcalibration_step = step - 1
            # ui_obj.pixelvalue_next_btn.setEnabled(True)
    # set image to UI
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    # camera_funcs.set_camera_picture_to_ui(ui_obj=ui_obj, ui_image_label=None, image=img, width_calibration=True)
    cv2.destroyAllWindows()
    # validate
    if step >= 5 and next:
        if succ:
            pxvalue_params = calibration_obj.solve_equation(infoes)
            # print(pxvalue_params)
            # apply to UI
            # ui_obj.pxvaluea_label.setText(pxvalue_params[0])
            # ui_obj.pxvalueb_label.setText(pxvalue_params[1])
            # ui_obj.pxvaluec_label.setText(pxvalue_params[2])
            # # # show message
            # ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.MESSEGES['pxvalue_calibration_apply'][ui_obj.language], level=0)
            # ui_obj.logger.create_new_log(message=texts.MESSEGES['pxvalue_calibration_apply']['en'], level=1)
            # # enable apply button
            # ui_obj.calib_save_params.setEnabled(True)
            print("Calibration Completed!")
            return True, pxvalue_params
        else:
            # show message
            return False, []


    

if __name__=='__main__':
    img = cv2.imread('calib_grading_N__.png')
    # cv2.imshow("img",cv2.resize(img, (0, 0), fx = 0.2, fy = 0.2))
    # cv2.waitKey(100)
    print(apply_pxvalue_calibration(img, True, True))