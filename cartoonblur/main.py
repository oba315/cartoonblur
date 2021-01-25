# coding:shift-JIS
# pylint: disable=F0401

import pymel.core as pm

import sys
sys.path.append(u"C:/Work/programming_semi/Script")

from . import cartoonBlur
reload (cartoonBlur)

#windowが開かれていたら閉じる
if pm.window('CBwin', ex=1) == True:
	pm.deleteUI('CBwin')

# - - - - UI - - - - 
with pm.window("CBwin", title="CartoonBlur", width=300 ) as CBwin:
    with pm.columnLayout( adjustableColumn=True, rowSpacing=5):
        
        pm.separator(height=20, style ="double")

        pm.button (label = "make vertex color set", c ='makeVtxColorSet( pm.PyNode( source.getText() ) )')


        pm.separator(height=20, style ="double")

        #?p?????[?^?????A???C???????????s
        pm.text( label='Setting' )
        source = pm.textFieldGrp( label='targetObject', text="pCylinder1" )
        times = pm.intFieldGrp( numberOfFields = 2, label='start-end Time',
                                value1 = 0, value2 = 10)
        #pm.radioCollection()
        useVertexGrp = pm.checkBoxGrp( numberOfCheckBoxes =1, label='using vertex color', value1=0)
        extends = pm.floatSliderGrp( label='extend', field=True, \
                    minValue=0.0, maxValue=10.0, fieldMinValue=0.0,\
                    fieldMaxValue=100.0, value=1.0)
        pm.button (
            label = "start",
            c = lambda *args: cartoonBlur.cartoonBlur(
                    source.getText(),
                    times.getValue()[0],
                    times.getValue()[1],
                    extends.getValue(),
                    useVertexGrp.getValueArray4()[0]
                    )
        )

pm.showWindow( CBwin )

