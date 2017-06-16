import numpy as np
import cv2

from rank import rank_inf as rank_filter_inf
from rank import rank_sup as rank_filter_sup
from PIL import Image
from primitive import *

# V2 : variable de debug permettant de controler la sauvegarde ou non de tous les produits intermediaires
debug = 0

# V2 : nouvelle version
def conv2SepMatlabbis(I,fen):
    #col, row = I.shape[1], I.shape[0]    
    rad = fen.size/2;
    
    I = cv2.copyMakeBorder(I,rad,rad,rad,rad,cv2.BORDER_CONSTANT,value=0)
    res = conv2bis(conv2bis(I,fen.T),fen); 
    return res

# pas verifiee
def FolkiIter(I0, I1, iteration = 5, radius = 8, talon = 1.e-8, uinit = None, vinit = None):
  
    W = lambda x : conv2Sep(x, np.ones([2*radius+1,1]) / 2*radius + 1)
    I0 = I0.astype(np.float32)
    I1 = I1.astype(np.float32)
    if uinit is None:
        u = np.zeros(I0.shape)
    else:
        u = uinit
    if vinit is None:
        v = np.zeros(I1.shape)
    else:
        v = vinit
    Ix, Iy = gradients(I0)
    Ixx = W(Ix*Ix) + talon
    Iyy = W(Iy*Iy) + talon
    Ixy = W(Ix*Iy)
    D   = Ixx*Iyy - Ixy**2
    cols, rows = I0.shape[1], I0.shape[0]
    x, y = np.meshgrid(range(cols), range(rows))
    for i in range(iteration):
        i1w = interp2(I1,x+u,y+v)
        it = I0 - i1w + u*Ix + v*Iy
        Ixt = W(Ix * it)
        Iyt = W(Iy * it)
        u = (Iyy * Ixt - Ixy * Iyt)/ D
        v = (Ixx * Iyt - Ixy * Ixt) /D
        unvalid = np.isnan(u)|np.isinf(u)|np.isnan(v)|np.isinf(v)
        u[unvalid] = 0
        v[unvalid] = 0
    return u,v



def EFolkiIter(I0, I1, iteration = 5, radius = [8, 4], rank = 4, uinit = None, vinit = None):
   
    #V2 : pour le debug   
    if debug:
	    eti = I0.shape[1]
	    img_to_save = Image.fromarray(I0)
	    name = '/home/janez/Tmp/im_avnt_rank'+str(eti)+'.tif'
	    img_to_save.save(name)
   

    if rank > 0:
        # V2 : dans version matlab on prend le sup 
	  #I0 = rank_filter_inf(I0, rank)
        I0 = rank_filter_sup(I0, rank)
        #I1 = rank_filter_inf(I1, rank)
        I1 = rank_filter_sup(I1, rank)
 
    if uinit is None:
        u = np.zeros(I0.shape)
    else:
        u = uinit
    if vinit is None:
        v = np.zeros(I1.shape)
    else:
        v = vinit

    #V2 
    # Ix, Iy = gradients(I0)
    Iy, Ix = np.gradient(I0)	

    #V2
    if debug:
    	    eti = I0.shape[1]
	    img_to_save = Image.fromarray(I0)
	    name = '/home/janez/Tmp/imrang'+str(eti)+'.tif'
	    img_to_save.save(name)
    
	    eti = I0.shape[1]
	    img_to_save = Image.fromarray(Ix)
	    name = '/home/janez/Tmp/gradx'+str(eti)+'.tif'
	    img_to_save.save(name)
    
	    eti = I0.shape[1]
	    img_to_save = Image.fromarray(Iy)
	    name = '/home/janez/Tmp/grady'+str(eti)+'.tif'
	    img_to_save.save(name)
 
    cols, rows = I0.shape[1], I0.shape[0]
    x, y = np.meshgrid(range(cols), range(rows))
    
    
    # uniquement pour debug et sauvegarde des produits intermediaires
    compt=1
    for rad in radius:
        # V2
        #W = lambda x : conv2Sep(x, np.ones([2*rad+1,1]) / 2*rad + 1)
        #W = lambda x : conv2Sep(x, np.ones([2*rad+1,1]))
        #W = lambda x : conv2SepMatlabbis(x, np.ones([2*rad+1,1]))
	burt1D = np.array(np.ones([1,2*rad+1]))
        W = lambda x : conv2SepMatlabbis(x,burt1D)
 
        
	
        Ixx = W(Ix*Ix)
        Iyy = W(Iy*Iy)
        Ixy = W(Ix*Iy)  
        D   = Ixx*Iyy - Ixy**2
      
        if debug:
            eti = Ixx.shape[1]
            img_to_save = Image.fromarray(Ixx)
            name = '/home/janez/Tmp/Ixx'+str(eti)+'.tif'
            img_to_save.save(name)
            compt=compt+1
  
        for i in range(iteration):
            i1w = interp2(I1,x+u,y+v)

            if debug:
		    eti = i1w.shape[1]
   		    img_to_save = Image.fromarray(i1w)
		    name = '/home/janez/Tmp/Ixx'+str(eti)+'-'+str(i)+'.tif'
   		    img_to_save.save(name)
	   

            it = I0 - i1w + u*Ix + v*Iy
            Ixt = W(Ix * it)
            Iyt = W(Iy * it)
            u = (Iyy * Ixt - Ixy * Iyt)/ D
            v = (Ixx * Iyt - Ixy * Ixt) /D
            unvalid = np.isnan(u)|np.isinf(u)|np.isnan(v)|np.isinf(v)
            u[unvalid] = 0
            v[unvalid] = 0
    return u,v

# pas verifiee
def GEFolkiIter(I0, I1, iteration = 5, radius = [8, 4], rank = 4, uinit = None, vinit = None):
    if rank > 0:
        R0 = rank_filter_sup(I0, rank)
        R1i = rank_filter_inf(I1, rank)
        R1s = rank_filter_sup(I1, rank)
    if uinit is None:
        u = np.zeros(I0.shape)
    else:
        u = uinit
    if vinit is None:
        v = np.zeros(I1.shape)
    else:
        v = vinit

    #V2
    #Ix, Iy = gradients(R0)
    Iy, Ix = np.gradient(I0)

    cols, rows = I0.shape[1], I0.shape[0]
    x, y = np.meshgrid(range(cols), range(rows))
    for rad in radius:
	#V2        
	#W = lambda x : conv2Sep(x, np.ones([2*rad+1,1]) / 2*rad + 1)
	burt1D = np.array(np.ones([1,2*rad+1]))
	W = lambda x : conv2SepMatlabbis(x,burt1D)

        Ixx = W(Ix*Ix)
        Iyy = W(Iy*Iy)
        Ixy = W(Ix*Iy)
        D   = Ixx*Iyy - Ixy**2
        for i in range(iteration):
            I1w = interp2(I1,x+u,y+v)
            #crit1 = conv2Sep(np.abs(I0-I1w), np.ones([2*rank+1,1]))
            #crit2 = conv2Sep(np.abs(1-I0-I1w), np.ones([2*rank+1,1]))
            crit1 = conv2SepMatlabbis(np.abs(I0-I1w), np.ones([2*rank+1,1]))
            crit2 = conv2SepMatlabbis(np.abs(1-I0-I1w), np.ones([2*rank+1,1]))


            R1w = interp2(R1s,x+u,y+v)
            R1w_1 = interp2(R1i,x+u,y+v)
            R1w[crit1 > crit2] = R1w_1[crit1 > crit2]
            it = R0 - R1w + u*Ix + v*Iy
            Ixt = W(Ix * it)
            Iyt = W(Iy * it)
            u = (Iyy * Ixt - Ixy * Iyt)/ D
            v = (Ixx * Iyt - Ixy * Ixt) /D
            unvalid = np.isnan(u)|np.isinf(u)|np.isnan(v)|np.isinf(v)
            u[unvalid] = 0
            v[unvalid] = 0
    return u,v


