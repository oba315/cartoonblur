# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm
import random

######  ????????  ####################################
#source_name = 'pCylinder1'
#obj = pm.PyNode(source_name)    #Transform???擾?????
#pm.select(source_name)
#ts = 0                          #?J?n?t???[??
#te = 24                          #?I???t???[??
#extend = 1                       #?i?s????????????????????
#####################################################




#?i?s????????????_??u??v?Z
def checkVtxPosition( obj, index, velocity ,obj_v_len, type = 'normal'):

    if type == 'dot':
        vp = obj.vtx[index].getPosition(space = 'world')
        for j in range(0, obj_v_len):
            if j == index:
                continue
            vother = obj.vtx[j].getPosition(space = 'world')
            if velocity.dot( vother-vp ) < 0:
                return 0
        return 1

    if type == 'normal':
        #???_???????ω??????@????velocity???r????
        #?X???[?Y?G?b?W??????obj.vtx[index].getNormals[0]??OK,???ω???K?v???
        nomls = obj.vtx[index].getNormals()

        #print index, len(nomls)
        if len(nomls) == 0:
            return 0
        nom = [0.0,0.0,0.0]
        for nomp in nomls:
            nom = nom+nomp
        nom[0] = nom[0] / len(nomls)
        nom[1] = nom[1] / len(nomls)
        nom[2] = nom[2] / len(nomls)


        ret = velocity.dot(nom)
        return ret*-1 if ret<0 else 0



#?????J???[?Z?b?g????ColorMa????????(???_?J???[??e???????w??)
#????(1)?A?????i0?j
def makeVColorMask(obj,obj_v_len):

    #?J???[?Z?b?g??擾
    pm.polyColorSet(obj, currentColorSet=True, colorSet= 'colorSet_for_cartoonBlur' )
    temp = pm.polyColorSet( query=True, currentColorSet=True )

    vColorMask = [
        1 - (sum(pm.polyColorPerVertex( obj.vtx[i],q=True,r=True,g=True,b=True ))/3 )
        for i in range(0,obj_v_len) ]

    print(vColorMask)
    return vColorMask



def makeVtxColorSet(obj):
    #???2????ColorSet?????m?F
    colSetLis = pm.polyColorSet(obj, query=1, allColorSets=1)
    if type(colSetLis) == list and u'colorSet_for_cartoonBlur' in pm.polyColorSet(obj, query=1, allColorSets=1):
        pm.polyColorSet( colorSet = 'colorSet_for_cartoonBlur', delete = 1)
        pm.confirmDialog( title="CartoonBlur", message="Vertex color set 'colorSet_for_cartoonBlur' is already exsist./Overwrited")

    pm.polyColorSet(obj, create = 1, rpt = "RGB", colorSet = 'colorSet_for_cartoonBlur')
    pm.polyColorPerVertex (obj, rgb = (1.0,1.0,1.0) )
    pm.confirmDialog( title="CartoonBlur", message="???_?J???[?fcolorSet_for_cartoonBlur?f??????h??????????G?t?F?N?g???????????B\n?????x????????????????x???????????????????o?O????????")


def cartoonBlur(source_name, ts, te, extend, use_vertexGrp):

    print " - - - cartoonblur - - - "
    print "frame : ", ts, te
    print "extend : ", extend
    print "use vertexFrp : ",use_vertexGrp 

    start = pm.timerX()
    percent = 0
    progressUnit =  int( 100 / (te-ts) )
    pm.progressWindow( title="CartoonBlur",
                        progress=percent,
                         status="please wait",
                          isInterruptable=True )



    obj = pm.PyNode(source_name)    
    pm.select(source_name)

    obj_v_len = len( obj.getPoints() )
    pm.blendShape(n='cartoonBlur')        #select?????


    #?????_???}?X?N????(????\??)
    randMask = [random.random() for i in range(0,obj_v_len) ]

    pm.currentTime(ts)
    # 頂点の位置を記憶
    Vbuffer = [obj.vtx[i].getPosition(space = "world") for i in range(0,obj_v_len)]

    # 頂点カラーによってマスク
    if use_vertexGrp == 1 :
        vColorMask = makeVColorMask(obj, obj_v_len)
    else :
        vColorMask = [ 1 for i in range(0,obj_v_len) ]


    for time in range(ts,te+1):

        pm.currentTime(time)


        # オブジェクトを複製，ブレンドシェイプターゲットとして設定
        target_name = obj + '_cartoonBlur_' + str(time)
        if pm.objExists(target_name):
            pm.delete( target_name )
        target = pm.duplicate(obj, n= target_name)[0]

        pm.blendShape( 'cartoonBlur', e=True, t=[source_name, time, target_name, 1])
        pm.hide(target)

        i = 0
        for i in range(0,obj_v_len):                    

            if vColorMask[i] == 0:
                continue

            vn = obj.vtx[i]
            vp = vn.getPosition(space = 'world')        #???_???W??擾

            vpprev = Vbuffer[i]

            vel_dir = ( vp - vpprev ).normal()          #???_????????
            vel_abs = ( vp - vpprev ).length()          #???_??????


            #target????_?????
            x = checkVtxPosition(obj, i, vel_dir, obj_v_len)\
                        * vel_abs * vel_dir * (-1) * extend\
                        * randMask[i]\
                        * vColorMask[i]
            target.vtx[i].setPosition(vp+x, space='world')

        #?O????_???o????
        Vbuffer = [obj.vtx[k].getPosition(space = "world") for k in range(0,obj_v_len)]

            #?L?[?t???[??????
        pm.setKeyframe('cartoonBlur.w['+str(time)+']', t=time-1, v=0)
        pm.setKeyframe('cartoonBlur.w['+str(time)+']', t=time, v=1)
        pm.setKeyframe('cartoonBlur.w['+str(time)+']', t=time+1, v=0)

        #?i?s?x?o?[??\???AESC????s????~
        if pm.progressWindow( query=True, isCancelled=True ):
            break
        percent += progressUnit
        pm.progressWindow(e=True, progress=percent, status='please wait')


    pm.progressWindow( endProgress=True )
    print "processing time:" + str(pm.timerX(startTime = start)) + "s"
