<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:2b184265-c956-4855-81aa-7c6f79be0a40(nltps.roles.physics.editor)">
  <persistence version="9" />
  <languages>
    <use id="18bc6592-03a6-4e29-a83a-7ff23bde13ba" name="jetbrains.mps.lang.editor" version="15" />
    <use id="aee9cad2-acd4-4608-aef2-0004f6a1cdbd" name="jetbrains.mps.lang.actions" version="4" />
    <devkit ref="fbc25dd2-5da4-483a-8b19-70928e1b62d7(jetbrains.mps.devkit.general-purpose)" />
  </languages>
  <imports>
    <import index="jb6s" ref="r:4741d84b-80d0-4a09-848d-cb03c7811725(nltps.clinicalintent.structure)" />
    <import index="7fnt" ref="r:863b484b-e576-4ac1-8523-3f82d6179201(nltps.roles.physics.structure)" implicit="true" />
    <import index="vyi7" ref="r:03c59dbb-02a2-4640-9787-a2fad5bd196e(nltps.roles.common.structure)" implicit="true" />
  </imports>
  <registry>
    <language id="18bc6592-03a6-4e29-a83a-7ff23bde13ba" name="jetbrains.mps.lang.editor">
      <concept id="1071666914219" name="jetbrains.mps.lang.editor.structure.ConceptEditorDeclaration" flags="ig" index="24kQdi" />
      <concept id="1140524381322" name="jetbrains.mps.lang.editor.structure.CellModel_ListWithRole" flags="ng" index="2czfm3">
        <child id="1140524464360" name="cellLayout" index="2czzBx" />
      </concept>
      <concept id="1237303669825" name="jetbrains.mps.lang.editor.structure.CellLayout_Indent" flags="nn" index="l2Vlx" />
      <concept id="1237307900041" name="jetbrains.mps.lang.editor.structure.IndentLayoutIndentStyleClassItem" flags="ln" index="lj46D" />
      <concept id="1237375020029" name="jetbrains.mps.lang.editor.structure.IndentLayoutNewLineChildrenStyleClassItem" flags="ln" index="pj6Ft" />
      <concept id="1237385578942" name="jetbrains.mps.lang.editor.structure.IndentLayoutOnNewLineStyleClassItem" flags="ln" index="pVoyu" />
      <concept id="1080736578640" name="jetbrains.mps.lang.editor.structure.BaseEditorComponent" flags="ig" index="2wURMF">
        <child id="1080736633877" name="cellModel" index="2wV5jI" />
      </concept>
      <concept id="1186414536763" name="jetbrains.mps.lang.editor.structure.BooleanStyleSheetItem" flags="ln" index="VOi$J">
        <property id="1186414551515" name="flag" index="VOm3f" />
      </concept>
      <concept id="1088013125922" name="jetbrains.mps.lang.editor.structure.CellModel_RefCell" flags="sg" stub="730538219795941030" index="1iCGBv">
        <child id="1088186146602" name="editorComponent" index="1sWHZn" />
      </concept>
      <concept id="1088185857835" name="jetbrains.mps.lang.editor.structure.InlineEditorComponent" flags="ig" index="1sVBvm" />
      <concept id="1139848536355" name="jetbrains.mps.lang.editor.structure.CellModel_WithRole" flags="ng" index="1$h60E">
        <property id="1140017977771" name="readOnly" index="1Intyy" />
        <reference id="1140103550593" name="relationDeclaration" index="1NtTu8" />
      </concept>
      <concept id="1073389446423" name="jetbrains.mps.lang.editor.structure.CellModel_Collection" flags="sn" stub="3013115976261988961" index="3EZMnI">
        <child id="1106270802874" name="cellLayout" index="2iSdaV" />
        <child id="1073389446424" name="childCellModel" index="3EZMnx" />
      </concept>
      <concept id="1073389577006" name="jetbrains.mps.lang.editor.structure.CellModel_Constant" flags="sn" stub="3610246225209162225" index="3F0ifn">
        <property id="1073389577007" name="text" index="3F0ifm" />
      </concept>
      <concept id="1073389658414" name="jetbrains.mps.lang.editor.structure.CellModel_Property" flags="sg" stub="730538219796134133" index="3F0A7n" />
      <concept id="1219418625346" name="jetbrains.mps.lang.editor.structure.IStyleContainer" flags="ngI" index="3F0Thp">
        <child id="1219418656006" name="styleItem" index="3F10Kt" />
      </concept>
      <concept id="1073390211982" name="jetbrains.mps.lang.editor.structure.CellModel_RefNodeList" flags="sg" stub="2794558372793454595" index="3F2HdR" />
      <concept id="1166049232041" name="jetbrains.mps.lang.editor.structure.AbstractComponent" flags="ng" index="1XWOmA">
        <reference id="1166049300910" name="conceptDeclaration" index="1XX52x" />
      </concept>
    </language>
  </registry>
  <node concept="24kQdi" id="1bNmcZ3taVB">
    <ref role="1XX52x" to="7fnt:1bNmcZ3oT9d" resolve="PhysicsProjection" />
    <node concept="3EZMnI" id="1bNmcZ3taVD" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ3taVE" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ3taVF" role="3EZMnx">
        <property role="3F0ifm" value="projectionName:" />
        <node concept="pVoyu" id="1bNmcZ3taVG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ3taVH" role="3EZMnx">
        <ref role="1NtTu8" to="vyi7:1bNmcZ2XUBp" resolve="projectionName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taVI" role="3EZMnx">
        <property role="3F0ifm" value="intendedRole:" />
        <node concept="pVoyu" id="1bNmcZ3taVJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ3taVK" role="3EZMnx">
        <ref role="1NtTu8" to="7fnt:1bNmcZ3oT9j" resolve="intendedRole" />
        <node concept="1sVBvm" id="1bNmcZ3taVN" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ3taVT" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAs" resolve="title" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taVV" role="3EZMnx">
        <property role="3F0ifm" value="views:" />
        <node concept="pVoyu" id="1bNmcZ3taVW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ3taVX" role="3EZMnx">
        <ref role="1NtTu8" to="7fnt:1bNmcZ3oT9h" resolve="views" />
        <node concept="pVoyu" id="1bNmcZ3taVZ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ3taW0" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ3taW1" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ3taW2" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taW4" role="3EZMnx">
        <property role="3F0ifm" value="tasks:" />
        <node concept="pVoyu" id="1bNmcZ3taW5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ3taW6" role="3EZMnx">
        <ref role="1NtTu8" to="7fnt:1bNmcZ3oT9i" resolve="tasks" />
        <node concept="pVoyu" id="1bNmcZ3taW8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ3taW9" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ3taWa" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ3taWb" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ3taWo">
    <ref role="1XX52x" to="7fnt:1bNmcZ3oT9b" resolve="PhysicsView" />
    <node concept="3EZMnI" id="1bNmcZ3taWq" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ3taWr" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ3taWs" role="3EZMnx">
        <property role="3F0ifm" value="viewName:" />
        <node concept="pVoyu" id="1bNmcZ3taWt" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ3taWu" role="3EZMnx">
        <ref role="1NtTu8" to="7fnt:1bNmcZ3oT9e" resolve="viewName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taWv" role="3EZMnx">
        <property role="3F0ifm" value="subjects:" />
        <node concept="pVoyu" id="1bNmcZ3taWw" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ3taWx" role="3EZMnx">
        <ref role="1NtTu8" to="7fnt:1bNmcZ3oT9f" resolve="subjects" />
        <node concept="pVoyu" id="1bNmcZ3taWz" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ3taW$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ3taW_" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ3taWA" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ3taWN">
    <ref role="1XX52x" to="7fnt:1bNmcZ3oT9c" resolve="PhysicsTask" />
    <node concept="3EZMnI" id="1bNmcZ3taWP" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ3taWQ" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ3taWR" role="3EZMnx">
        <property role="3F0ifm" value="taskKind:" />
        <node concept="pVoyu" id="1bNmcZ3taWS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ3taWT" role="3EZMnx">
        <ref role="1NtTu8" to="7fnt:1bNmcZ3oT9g" resolve="taskKind" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taWU" role="3EZMnx">
        <property role="3F0ifm" value="commandName:" />
        <node concept="pVoyu" id="1bNmcZ3taWV" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ3taWW" role="3EZMnx">
        <ref role="1NtTu8" to="vyi7:1bNmcZ2XUBx" resolve="commandName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taWX" role="3EZMnx">
        <property role="3F0ifm" value="targets:" />
        <node concept="pVoyu" id="1bNmcZ3taWY" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ3taWZ" role="3EZMnx">
        <ref role="1NtTu8" to="vyi7:1bNmcZ2XUBy" resolve="targets" />
        <node concept="pVoyu" id="1bNmcZ3taX1" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ3taX2" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ3taX3" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ3taX4" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taX6" role="3EZMnx">
        <property role="3F0ifm" value="actions:" />
        <node concept="pVoyu" id="1bNmcZ3taX7" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ3taX8" role="3EZMnx">
        <ref role="1NtTu8" to="vyi7:1bNmcZ2XUBz" resolve="actions" />
        <node concept="pVoyu" id="1bNmcZ3taXa" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ3taXb" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ3taXc" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ3taXd" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taXf" role="3EZMnx">
        <property role="3F0ifm" value="states:" />
        <node concept="pVoyu" id="1bNmcZ3taXg" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ3taXh" role="3EZMnx">
        <ref role="1NtTu8" to="vyi7:1bNmcZ2XUB$" resolve="states" />
        <node concept="pVoyu" id="1bNmcZ3taXj" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ3taXk" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ3taXl" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ3taXm" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ3taXo" role="3EZMnx">
        <property role="3F0ifm" value="roles:" />
        <node concept="pVoyu" id="1bNmcZ3taXp" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ3taXq" role="3EZMnx">
        <ref role="1NtTu8" to="vyi7:1bNmcZ2XUB_" resolve="roles" />
        <node concept="pVoyu" id="1bNmcZ3taXs" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ3taXt" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ3taXu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ3taXv" role="2czzBx" />
      </node>
    </node>
  </node>
</model>

