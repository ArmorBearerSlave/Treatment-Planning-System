<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:55a5c852-932b-4796-bd64-9279e896dd77(nltps.clinicalintent.editor)">
  <persistence version="9" />
  <languages>
    <use id="18bc6592-03a6-4e29-a83a-7ff23bde13ba" name="jetbrains.mps.lang.editor" version="15" />
    <use id="aee9cad2-acd4-4608-aef2-0004f6a1cdbd" name="jetbrains.mps.lang.actions" version="4" />
    <devkit ref="fbc25dd2-5da4-483a-8b19-70928e1b62d7(jetbrains.mps.devkit.general-purpose)" />
  </languages>
  <imports>
    <import index="5q6" ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)" />
    <import index="jb6s" ref="r:4741d84b-80d0-4a09-848d-cb03c7811725(nltps.clinicalintent.structure)" />
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
      <concept id="1073389882823" name="jetbrains.mps.lang.editor.structure.CellModel_RefNode" flags="sg" stub="730538219795960754" index="3F1sOY" />
      <concept id="1073390211982" name="jetbrains.mps.lang.editor.structure.CellModel_RefNodeList" flags="sg" stub="2794558372793454595" index="3F2HdR" />
      <concept id="1166049232041" name="jetbrains.mps.lang.editor.structure.AbstractComponent" flags="ng" index="1XWOmA">
        <reference id="1166049300910" name="conceptDeclaration" index="1XX52x" />
      </concept>
    </language>
  </registry>
  <node concept="24kQdi" id="1bNmcZ2XW0G">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUA$" resolve="PlanIntentDefinition" />
    <node concept="3EZMnI" id="1bNmcZ2XW0I" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XW0J" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XW0K" role="3EZMnx">
        <property role="3F0ifm" value="Name:" />
        <node concept="pVoyu" id="1bNmcZ2XW0L" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW0M" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAL" resolve="name" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW0N" role="3EZMnx">
        <property role="3F0ifm" value="aiCreatable:" />
        <node concept="pVoyu" id="1bNmcZ2XW0O" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW0P" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAM" resolve="aiCreatable" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW0Q" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XW0R" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW0S" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XW0V" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW11" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW13" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XW14" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW15" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XW18" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW1e" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW1g" role="3EZMnx">
        <property role="3F0ifm" value="objectTypes:" />
        <node concept="pVoyu" id="1bNmcZ2XW1h" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW1i" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAN" resolve="objectTypes" />
        <node concept="pVoyu" id="1bNmcZ2XW1k" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW1l" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW1m" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW1n" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW1p" role="3EZMnx">
        <property role="3F0ifm" value="actions:" />
        <node concept="pVoyu" id="1bNmcZ2XW1q" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW1r" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAO" resolve="actions" />
        <node concept="pVoyu" id="1bNmcZ2XW1t" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW1u" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW1v" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW1w" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW1y" role="3EZMnx">
        <property role="3F0ifm" value="constraints:" />
        <node concept="pVoyu" id="1bNmcZ2XW1z" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW1$" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAP" resolve="constraints" />
        <node concept="pVoyu" id="1bNmcZ2XW1A" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW1B" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW1C" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW1D" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW1F" role="3EZMnx">
        <property role="3F0ifm" value="robustnessScenarios:" />
        <node concept="pVoyu" id="1bNmcZ2XW1G" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW1H" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAQ" resolve="robustnessScenarios" />
        <node concept="pVoyu" id="1bNmcZ2XW1J" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW1K" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW1L" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW1M" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW1O" role="3EZMnx">
        <property role="3F0ifm" value="operatingModes:" />
        <node concept="pVoyu" id="1bNmcZ2XW1P" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW1Q" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAR" resolve="operatingModes" />
        <node concept="pVoyu" id="1bNmcZ2XW1S" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW1T" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW1U" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW1V" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW1X" role="3EZMnx">
        <property role="3F0ifm" value="computableRules:" />
        <node concept="pVoyu" id="1bNmcZ2XW1Y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW1Z" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAS" resolve="computableRules" />
        <node concept="pVoyu" id="1bNmcZ2XW21" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW22" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW23" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW24" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW26" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XW27" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW28" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XW29" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW2a" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW2b" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XW2c" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW2d" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XW2e" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW2f" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW2g" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XW2h" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW2i" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XW2k" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW2l" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW2m" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW2n" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW2p" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XW2q" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW2r" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XW2t" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW2u" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW2v" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW2w" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XW2H">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUA_" resolve="AuthorityPolicy" />
    <node concept="3EZMnI" id="1bNmcZ2XW2J" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XW2K" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XW2L" role="3EZMnx">
        <property role="3F0ifm" value="Name:" />
        <node concept="pVoyu" id="1bNmcZ2XW2M" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW2N" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAT" resolve="name" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW2O" role="3EZMnx">
        <property role="3F0ifm" value="institution:" />
        <node concept="pVoyu" id="1bNmcZ2XW2P" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW2Q" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAU" resolve="institution" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW2R" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XW2S" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW2T" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XW2W" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW32" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW34" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XW35" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW36" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XW39" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW3f" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW3h" role="3EZMnx">
        <property role="3F0ifm" value="professionalRoles:" />
        <node concept="pVoyu" id="1bNmcZ2XW3i" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW3j" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAV" resolve="professionalRoles" />
        <node concept="pVoyu" id="1bNmcZ2XW3l" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW3m" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW3n" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW3o" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW3q" role="3EZMnx">
        <property role="3F0ifm" value="operationalRoles:" />
        <node concept="pVoyu" id="1bNmcZ2XW3r" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW3s" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAW" resolve="operationalRoles" />
        <node concept="pVoyu" id="1bNmcZ2XW3u" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW3v" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW3w" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW3x" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW3z" role="3EZMnx">
        <property role="3F0ifm" value="capabilities:" />
        <node concept="pVoyu" id="1bNmcZ2XW3$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW3_" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAX" resolve="capabilities" />
        <node concept="pVoyu" id="1bNmcZ2XW3B" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW3C" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW3D" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW3E" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW3G" role="3EZMnx">
        <property role="3F0ifm" value="actors:" />
        <node concept="pVoyu" id="1bNmcZ2XW3H" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW3I" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAY" resolve="actors" />
        <node concept="pVoyu" id="1bNmcZ2XW3K" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW3L" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW3M" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW3N" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW3P" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XW3Q" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW3R" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XW3S" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW3T" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW3U" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XW3V" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW3W" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XW3X" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW3Y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW3Z" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XW40" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW41" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XW43" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW44" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW45" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW46" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW48" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XW49" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW4a" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XW4c" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW4d" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW4e" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW4f" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XW4s">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUB9" resolve="WorkflowDefinition" />
    <node concept="3EZMnI" id="1bNmcZ2XW4u" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XW4v" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XW4w" role="3EZMnx">
        <property role="3F0ifm" value="Name:" />
        <node concept="pVoyu" id="1bNmcZ2XW4x" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW4y" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBf" resolve="name" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW4z" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XW4$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW4_" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XW4C" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW4I" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW4K" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XW4L" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW4M" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XW4P" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW4V" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW4X" role="3EZMnx">
        <property role="3F0ifm" value="states:" />
        <node concept="pVoyu" id="1bNmcZ2XW4Y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW4Z" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBg" resolve="states" />
        <node concept="pVoyu" id="1bNmcZ2XW51" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW52" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW53" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW54" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW56" role="3EZMnx">
        <property role="3F0ifm" value="transitions:" />
        <node concept="pVoyu" id="1bNmcZ2XW57" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW58" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBh" resolve="transitions" />
        <node concept="pVoyu" id="1bNmcZ2XW5a" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW5b" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW5c" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW5d" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW5f" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XW5g" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW5h" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XW5i" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW5j" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW5k" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XW5l" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW5m" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XW5n" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW5o" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW5p" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XW5q" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW5r" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XW5t" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW5u" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW5v" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW5w" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW5y" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XW5z" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW5$" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XW5A" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW5B" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW5C" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW5D" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XW5Q">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAA" resolve="ReleaseProfile" />
    <node concept="3EZMnI" id="1bNmcZ2XW5S" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XW5T" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XW5U" role="3EZMnx">
        <property role="3F0ifm" value="Name:" />
        <node concept="pVoyu" id="1bNmcZ2XW5V" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW5W" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAZ" resolve="name" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW5X" role="3EZMnx">
        <property role="3F0ifm" value="intendedUse:" />
        <node concept="pVoyu" id="1bNmcZ2XW5Y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW5Z" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUB0" resolve="intendedUse" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW60" role="3EZMnx">
        <property role="3F0ifm" value="releaseState:" />
        <node concept="pVoyu" id="1bNmcZ2XW61" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW62" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUB1" resolve="releaseState" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW63" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XW64" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW65" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XW68" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW6e" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW6g" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XW6h" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW6i" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XW6l" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW6r" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW6t" role="3EZMnx">
        <property role="3F0ifm" value="evidenceProfiles:" />
        <node concept="pVoyu" id="1bNmcZ2XW6u" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW6v" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUB2" resolve="evidenceProfiles" />
        <node concept="pVoyu" id="1bNmcZ2XW6x" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW6y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW6z" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW6$" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW6A" role="3EZMnx">
        <property role="3F0ifm" value="commissionedUse:" />
        <node concept="pVoyu" id="1bNmcZ2XW6B" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW6C" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUB3" resolve="commissionedUse" />
        <node concept="pVoyu" id="1bNmcZ2XW6E" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW6F" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW6G" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW6H" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW6J" role="3EZMnx">
        <property role="3F0ifm" value="modelProfiles:" />
        <node concept="pVoyu" id="1bNmcZ2XW6K" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW6L" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUB4" resolve="modelProfiles" />
        <node concept="pVoyu" id="1bNmcZ2XW6N" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW6O" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW6P" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW6Q" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW6S" role="3EZMnx">
        <property role="3F0ifm" value="machineProfiles:" />
        <node concept="pVoyu" id="1bNmcZ2XW6T" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW6U" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUB5" resolve="machineProfiles" />
        <node concept="pVoyu" id="1bNmcZ2XW6W" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW6X" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW6Y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW6Z" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW71" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XW72" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW73" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XW74" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW75" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW76" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XW77" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW78" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XW79" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW7a" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW7b" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XW7c" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW7d" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XW7f" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW7g" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW7h" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW7i" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW7k" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XW7l" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW7m" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XW7o" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW7p" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW7q" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW7r" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XW7C">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_B" resolve="ClinicalObjectType" />
    <node concept="3EZMnI" id="1bNmcZ2XW7E" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XW7F" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XW7G" role="3EZMnx">
        <property role="3F0ifm" value="typeName:" />
        <node concept="pVoyu" id="1bNmcZ2XW7H" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW7I" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_C" resolve="typeName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW7J" role="3EZMnx">
        <property role="3F0ifm" value="description:" />
        <node concept="pVoyu" id="1bNmcZ2XW7K" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW7L" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_D" resolve="description" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW7M" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XW7N" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW7O" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XW7R" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW7X" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW7Z" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XW80" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW81" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XW84" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW8a" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW8c" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XW8d" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW8e" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XW8f" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW8g" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW8h" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XW8i" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW8j" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XW8k" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW8l" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW8m" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XW8n" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW8o" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XW8q" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW8r" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW8s" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW8t" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW8v" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XW8w" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW8x" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XW8z" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW8$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW8_" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW8A" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XW8N">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_G" resolve="ActionDefinition" />
    <node concept="3EZMnI" id="1bNmcZ2XW8P" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XW8Q" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XW8R" role="3EZMnx">
        <property role="3F0ifm" value="actionName:" />
        <node concept="pVoyu" id="1bNmcZ2XW8S" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW8T" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_I" resolve="actionName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW8U" role="3EZMnx">
        <property role="3F0ifm" value="autonomyLevel:" />
        <node concept="pVoyu" id="1bNmcZ2XW8V" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW8W" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_J" resolve="autonomyLevel" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW8X" role="3EZMnx">
        <property role="3F0ifm" value="description:" />
        <node concept="pVoyu" id="1bNmcZ2XW8Y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XW8Z" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_K" resolve="description" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW90" role="3EZMnx">
        <property role="3F0ifm" value="appliesTo:" />
        <node concept="pVoyu" id="1bNmcZ2XW91" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW92" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_L" resolve="appliesTo" />
        <node concept="1sVBvm" id="1bNmcZ2XW95" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW9b" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_C" resolve="typeName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW9d" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XW9e" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW9f" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XW9i" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW9o" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW9q" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XW9r" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XW9s" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XW9v" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XW9_" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW9B" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XW9C" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW9D" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XW9E" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW9F" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW9G" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XW9H" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XW9I" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XW9J" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW9K" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW9L" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XW9M" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW9N" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XW9P" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW9Q" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XW9R" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XW9S" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XW9U" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XW9V" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XW9W" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XW9Y" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XW9Z" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWa0" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWa1" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWae">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_H" resolve="ConstraintDefinition" />
    <node concept="3EZMnI" id="1bNmcZ2XWag" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWah" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWai" role="3EZMnx">
        <property role="3F0ifm" value="constraintName:" />
        <node concept="pVoyu" id="1bNmcZ2XWaj" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWak" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_M" resolve="constraintName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWal" role="3EZMnx">
        <property role="3F0ifm" value="comparison:" />
        <node concept="pVoyu" id="1bNmcZ2XWam" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWan" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_N" resolve="comparison" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWao" role="3EZMnx">
        <property role="3F0ifm" value="structure:" />
        <node concept="pVoyu" id="1bNmcZ2XWap" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWaq" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_O" resolve="structure" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWar" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWas" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWat" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWaw" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWaA" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWaC" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWaD" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWaE" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWaH" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWaN" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWaP" role="3EZMnx">
        <property role="3F0ifm" value="limit:" />
        <node concept="pVoyu" id="1bNmcZ2XWaQ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWaR" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_P" resolve="limit" />
        <node concept="pVoyu" id="1bNmcZ2XWaS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWaT" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWaU" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWaV" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWaW" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWaX" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWaY" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWaZ" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWb0" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWb1" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWb2" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWb3" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWb4" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWb5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWb6" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWb8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWb9" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWba" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWbb" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWbd" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWbe" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWbf" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWbh" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWbi" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWbj" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWbk" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWbx">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_V" resolve="RobustnessScenarioDefinition" />
    <node concept="3EZMnI" id="1bNmcZ2XWbz" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWb$" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWb_" role="3EZMnx">
        <property role="3F0ifm" value="scenarioName:" />
        <node concept="pVoyu" id="1bNmcZ2XWbA" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWbB" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA0" resolve="scenarioName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWbC" role="3EZMnx">
        <property role="3F0ifm" value="perturbation:" />
        <node concept="pVoyu" id="1bNmcZ2XWbD" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWbE" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA1" resolve="perturbation" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWbF" role="3EZMnx">
        <property role="3F0ifm" value="magnitudeDescription:" />
        <node concept="pVoyu" id="1bNmcZ2XWbG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWbH" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA2" resolve="magnitudeDescription" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWbI" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWbJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWbK" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWbN" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWbT" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWbV" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWbW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWbX" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWc0" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWc6" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWc8" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWc9" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWca" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWcb" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWcc" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWcd" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWce" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWcf" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWcg" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWch" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWci" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWcj" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWck" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWcm" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWcn" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWco" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWcp" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWcr" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWcs" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWct" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWcv" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWcw" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWcx" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWcy" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWcJ">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_W" resolve="OperatingMode" />
    <node concept="3EZMnI" id="1bNmcZ2XWcL" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWcM" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWcN" role="3EZMnx">
        <property role="3F0ifm" value="modeName:" />
        <node concept="pVoyu" id="1bNmcZ2XWcO" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWcP" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA3" resolve="modeName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWcQ" role="3EZMnx">
        <property role="3F0ifm" value="description:" />
        <node concept="pVoyu" id="1bNmcZ2XWcR" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWcS" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA4" resolve="description" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWcT" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWcU" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWcV" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWcY" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWd4" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWd6" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWd7" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWd8" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWdb" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWdh" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWdj" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWdk" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWdl" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWdm" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWdn" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWdo" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWdp" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWdq" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWdr" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWds" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWdt" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWdu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWdv" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWdx" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWdy" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWdz" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWd$" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWdA" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWdB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWdC" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWdE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWdF" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWdG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWdH" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWdU">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_X" resolve="ComputableRule" />
    <node concept="3EZMnI" id="1bNmcZ2XWdW" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWdX" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWdY" role="3EZMnx">
        <property role="3F0ifm" value="ruleName:" />
        <node concept="pVoyu" id="1bNmcZ2XWdZ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWe0" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA5" resolve="ruleName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWe1" role="3EZMnx">
        <property role="3F0ifm" value="expression:" />
        <node concept="pVoyu" id="1bNmcZ2XWe2" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWe3" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA6" resolve="expression" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWe4" role="3EZMnx">
        <property role="3F0ifm" value="evaluable:" />
        <node concept="pVoyu" id="1bNmcZ2XWe5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWe6" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA7" resolve="evaluable" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWe7" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWe8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWe9" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWec" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWei" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWek" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWel" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWem" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWep" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWev" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWex" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWey" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWez" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWe$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWe_" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWeA" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWeB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWeC" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWeD" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWeE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWeF" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWeG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWeH" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWeJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWeK" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWeL" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWeM" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWeO" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWeP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWeQ" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWeS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWeT" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWeU" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWeV" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWf8">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_Y" resolve="WorkflowState" />
    <node concept="3EZMnI" id="1bNmcZ2XWfa" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWfb" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWfc" role="3EZMnx">
        <property role="3F0ifm" value="stateName:" />
        <node concept="pVoyu" id="1bNmcZ2XWfd" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWfe" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA8" resolve="stateName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWff" role="3EZMnx">
        <property role="3F0ifm" value="terminal:" />
        <node concept="pVoyu" id="1bNmcZ2XWfg" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWfh" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA9" resolve="terminal" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWfi" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWfj" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWfk" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWfn" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWft" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWfv" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWfw" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWfx" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWf$" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWfE" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWfG" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWfH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWfI" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWfJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWfK" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWfL" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWfM" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWfN" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWfO" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWfP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWfQ" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWfR" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWfS" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWfU" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWfV" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWfW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWfX" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWfZ" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWg0" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWg1" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWg3" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWg4" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWg5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWg6" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWgj">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUB8" resolve="StateTransition" />
    <node concept="3EZMnI" id="1bNmcZ2XWgl" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWgm" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWgn" role="3EZMnx">
        <property role="3F0ifm" value="guard:" />
        <node concept="pVoyu" id="1bNmcZ2XWgo" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWgp" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBa" resolve="guard" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWgq" role="3EZMnx">
        <property role="3F0ifm" value="invalidationEffect:" />
        <node concept="pVoyu" id="1bNmcZ2XWgr" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWgs" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBb" resolve="invalidationEffect" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWgt" role="3EZMnx">
        <property role="3F0ifm" value="source:" />
        <node concept="pVoyu" id="1bNmcZ2XWgu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWgv" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBc" resolve="source" />
        <node concept="1sVBvm" id="1bNmcZ2XWgy" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWgC" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA8" resolve="stateName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWgE" role="3EZMnx">
        <property role="3F0ifm" value="target:" />
        <node concept="pVoyu" id="1bNmcZ2XWgF" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWgG" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBd" resolve="target" />
        <node concept="1sVBvm" id="1bNmcZ2XWgJ" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWgP" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA8" resolve="stateName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWgR" role="3EZMnx">
        <property role="3F0ifm" value="actorRole:" />
        <node concept="pVoyu" id="1bNmcZ2XWgS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWgT" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUBe" resolve="actorRole" />
        <node concept="1sVBvm" id="1bNmcZ2XWgW" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWh2" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAu" resolve="functionName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWh4" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWh5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWh6" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWh9" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWhf" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWhh" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWhi" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWhj" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWhm" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWhs" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWhu" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWhv" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWhw" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWhx" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWhy" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWhz" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWh$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWh_" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWhA" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWhB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWhC" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWhD" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWhE" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWhG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWhH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWhI" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWhJ" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWhL" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWhM" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWhN" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWhP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWhQ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWhR" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWhS" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWi5">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XU_Z" resolve="EvidenceProfile" />
    <node concept="3EZMnI" id="1bNmcZ2XWi7" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWi8" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWi9" role="3EZMnx">
        <property role="3F0ifm" value="profileName:" />
        <node concept="pVoyu" id="1bNmcZ2XWia" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWib" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAa" resolve="profileName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWic" role="3EZMnx">
        <property role="3F0ifm" value="requiredTier:" />
        <node concept="pVoyu" id="1bNmcZ2XWid" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWie" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAb" resolve="requiredTier" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWif" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWig" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWih" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWik" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWiq" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWis" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWit" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWiu" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWix" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWiB" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWiD" role="3EZMnx">
        <property role="3F0ifm" value="citations:" />
        <node concept="pVoyu" id="1bNmcZ2XWiE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWiF" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAc" resolve="citations" />
        <node concept="pVoyu" id="1bNmcZ2XWiH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWiI" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWiJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWiK" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWiM" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWiN" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWiO" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWiP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWiQ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWiR" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWiS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWiT" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWiU" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWiV" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWiW" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWiX" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWiY" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWj0" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWj1" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWj2" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWj3" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWj5" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWj6" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWj7" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWj9" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWja" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWjb" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWjc" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWjp">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAf" resolve="CommissionedUseEnvelope" />
    <node concept="3EZMnI" id="1bNmcZ2XWjr" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWjs" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWjt" role="3EZMnx">
        <property role="3F0ifm" value="envelopeName:" />
        <node concept="pVoyu" id="1bNmcZ2XWju" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWjv" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAk" resolve="envelopeName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWjw" role="3EZMnx">
        <property role="3F0ifm" value="scopeDescription:" />
        <node concept="pVoyu" id="1bNmcZ2XWjx" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWjy" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAl" resolve="scopeDescription" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWjz" role="3EZMnx">
        <property role="3F0ifm" value="commissionedOn:" />
        <node concept="pVoyu" id="1bNmcZ2XWj$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWj_" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAm" resolve="commissionedOn" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWjA" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWjB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWjC" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWjF" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWjL" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWjN" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWjO" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWjP" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWjS" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWjY" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWk0" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWk1" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWk2" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWk3" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWk4" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWk5" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWk6" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWk7" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWk8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWk9" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWka" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWkb" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWkc" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWke" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWkf" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWkg" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWkh" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWkj" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWkk" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWkl" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWkn" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWko" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWkp" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWkq" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWkB">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAg" resolve="ModelProfile" />
    <node concept="3EZMnI" id="1bNmcZ2XWkD" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWkE" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWkF" role="3EZMnx">
        <property role="3F0ifm" value="modelName:" />
        <node concept="pVoyu" id="1bNmcZ2XWkG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWkH" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAn" resolve="modelName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWkI" role="3EZMnx">
        <property role="3F0ifm" value="modelVersion:" />
        <node concept="pVoyu" id="1bNmcZ2XWkJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWkK" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAo" resolve="modelVersion" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWkL" role="3EZMnx">
        <property role="3F0ifm" value="validated:" />
        <node concept="pVoyu" id="1bNmcZ2XWkM" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWkN" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAp" resolve="validated" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWkO" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWkP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWkQ" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWkT" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWkZ" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWl1" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWl2" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWl3" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWl6" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWlc" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWle" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWlf" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWlg" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWlh" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWli" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWlj" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWlk" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWll" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWlm" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWln" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWlo" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWlp" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWlq" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWls" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWlt" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWlu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWlv" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWlx" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWly" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWlz" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWl_" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWlA" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWlB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWlC" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWlP">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAh" resolve="MachineProfile" />
    <node concept="3EZMnI" id="1bNmcZ2XWlR" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWlS" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWlT" role="3EZMnx">
        <property role="3F0ifm" value="machineName:" />
        <node concept="pVoyu" id="1bNmcZ2XWlU" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWlV" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAq" resolve="machineName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWlW" role="3EZMnx">
        <property role="3F0ifm" value="configuration:" />
        <node concept="pVoyu" id="1bNmcZ2XWlX" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWlY" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAr" resolve="configuration" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWlZ" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWm0" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWm1" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWm4" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWma" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWmc" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWmd" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWme" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWmh" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWmn" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWmp" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWmq" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWmr" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWms" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWmt" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWmu" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWmv" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWmw" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWmx" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWmy" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWmz" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWm$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWm_" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWmB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWmC" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWmD" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWmE" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWmG" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWmH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWmI" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWmK" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWmL" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWmM" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWmN" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWn0">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAi" resolve="ProfessionalRole" />
    <node concept="3EZMnI" id="1bNmcZ2XWn2" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWn3" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWn4" role="3EZMnx">
        <property role="3F0ifm" value="title:" />
        <node concept="pVoyu" id="1bNmcZ2XWn5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWn6" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAs" resolve="title" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWn7" role="3EZMnx">
        <property role="3F0ifm" value="credentialBasis:" />
        <node concept="pVoyu" id="1bNmcZ2XWn8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWn9" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAt" resolve="credentialBasis" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWna" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWnb" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWnc" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWnf" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWnl" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWnn" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWno" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWnp" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWns" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWny" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWn$" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWn_" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWnA" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWnB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWnC" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWnD" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWnE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWnF" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWnG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWnH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWnI" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWnJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWnK" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWnM" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWnN" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWnO" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWnP" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWnR" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWnS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWnT" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWnV" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWnW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWnX" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWnY" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWob">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAj" resolve="OperationalRole" />
    <node concept="3EZMnI" id="1bNmcZ2XWod" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWoe" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWof" role="3EZMnx">
        <property role="3F0ifm" value="functionName:" />
        <node concept="pVoyu" id="1bNmcZ2XWog" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWoh" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAu" resolve="functionName" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWoi" role="3EZMnx">
        <property role="3F0ifm" value="description:" />
        <node concept="pVoyu" id="1bNmcZ2XWoj" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWok" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAv" resolve="description" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWol" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWom" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWon" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWoq" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWow" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWoy" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWoz" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWo$" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWoB" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWoH" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWoJ" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWoK" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWoL" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWoM" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWoN" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWoO" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWoP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWoQ" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWoR" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWoS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWoT" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWoU" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWoV" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWoX" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWoY" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWoZ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWp0" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWp2" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWp3" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWp4" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWp6" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWp7" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWp8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWp9" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWpm">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAy" resolve="RoleCapability" />
    <node concept="3EZMnI" id="1bNmcZ2XWpo" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWpp" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWpq" role="3EZMnx">
        <property role="3F0ifm" value="requiresApproval:" />
        <node concept="pVoyu" id="1bNmcZ2XWpr" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWps" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAB" resolve="requiresApproval" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWpt" role="3EZMnx">
        <property role="3F0ifm" value="professionalRole:" />
        <node concept="pVoyu" id="1bNmcZ2XWpu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWpv" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAC" resolve="professionalRole" />
        <node concept="1sVBvm" id="1bNmcZ2XWpy" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWpC" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAs" resolve="title" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWpE" role="3EZMnx">
        <property role="3F0ifm" value="operationalRole:" />
        <node concept="pVoyu" id="1bNmcZ2XWpF" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWpG" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAD" resolve="operationalRole" />
        <node concept="1sVBvm" id="1bNmcZ2XWpJ" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWpP" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAu" resolve="functionName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWpR" role="3EZMnx">
        <property role="3F0ifm" value="allowedAction:" />
        <node concept="pVoyu" id="1bNmcZ2XWpS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWpT" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAE" resolve="allowedAction" />
        <node concept="1sVBvm" id="1bNmcZ2XWpW" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWq2" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_I" resolve="actionName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWq4" role="3EZMnx">
        <property role="3F0ifm" value="targetScope:" />
        <node concept="pVoyu" id="1bNmcZ2XWq5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWq6" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAF" resolve="targetScope" />
        <node concept="1sVBvm" id="1bNmcZ2XWq9" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWqf" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XU_C" resolve="typeName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWqh" role="3EZMnx">
        <property role="3F0ifm" value="workflowState:" />
        <node concept="pVoyu" id="1bNmcZ2XWqi" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWqj" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAG" resolve="workflowState" />
        <node concept="1sVBvm" id="1bNmcZ2XWqm" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWqs" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUA8" resolve="stateName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWqu" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWqv" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWqw" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWqz" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWqD" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWqF" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWqG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWqH" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWqK" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWqQ" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWqS" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWqT" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWqU" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWqV" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWqW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWqX" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWqY" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWqZ" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWr0" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWr1" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWr2" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWr3" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWr4" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWr6" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWr7" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWr8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWr9" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWrb" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWrc" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWrd" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWrf" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWrg" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWrh" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWri" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2XWrv">
    <ref role="1XX52x" to="jb6s:1bNmcZ2XUAz" resolve="AuthorizedActor" />
    <node concept="3EZMnI" id="1bNmcZ2XWrx" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2XWry" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2XWrz" role="3EZMnx">
        <property role="3F0ifm" value="principalId:" />
        <node concept="pVoyu" id="1bNmcZ2XWr$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWr_" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAH" resolve="principalId" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWrA" role="3EZMnx">
        <property role="3F0ifm" value="actorKind:" />
        <node concept="pVoyu" id="1bNmcZ2XWrB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2XWrC" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAI" resolve="actorKind" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWrD" role="3EZMnx">
        <property role="3F0ifm" value="professionalRole:" />
        <node concept="pVoyu" id="1bNmcZ2XWrE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWrF" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAJ" resolve="professionalRole" />
        <node concept="1sVBvm" id="1bNmcZ2XWrI" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWrO" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAs" resolve="title" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWrQ" role="3EZMnx">
        <property role="3F0ifm" value="operationalRole:" />
        <node concept="pVoyu" id="1bNmcZ2XWrR" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWrS" role="3EZMnx">
        <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAK" resolve="operationalRole" />
        <node concept="1sVBvm" id="1bNmcZ2XWrV" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWs1" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="jb6s:1bNmcZ2XUAu" resolve="functionName" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWs3" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2XWs4" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWs5" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2XWs8" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWse" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWsg" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2XWsh" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2XWsi" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2XWsl" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2XWsr" role="2wV5jI">
            <property role="1Intyy" value="true" />
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWst" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2XWsu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWsv" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2XWsw" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWsx" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWsy" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2XWsz" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2XWs$" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2XWs_" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWsA" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWsB" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2XWsC" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWsD" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2XWsF" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWsG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWsH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWsI" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2XWsK" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2XWsL" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2XWsM" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2XWsO" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2XWsP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2XWsQ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2XWsR" role="2czzBx" />
      </node>
    </node>
  </node>
</model>

