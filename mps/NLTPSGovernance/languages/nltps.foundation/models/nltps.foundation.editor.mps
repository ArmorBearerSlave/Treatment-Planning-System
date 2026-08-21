<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:7d8d955d-696e-4941-845d-8340bbbc14b8(nltps.foundation.editor)">
  <persistence version="9" />
  <languages>
    <use id="18bc6592-03a6-4e29-a83a-7ff23bde13ba" name="jetbrains.mps.lang.editor" version="15" />
    <use id="aee9cad2-acd4-4608-aef2-0004f6a1cdbd" name="jetbrains.mps.lang.actions" version="4" />
    <devkit ref="fbc25dd2-5da4-483a-8b19-70928e1b62d7(jetbrains.mps.devkit.general-purpose)" />
  </languages>
  <imports>
    <import index="5q6" ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)" />
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
  <node concept="24kQdi" id="1bNmcZ2iUfW">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsw" resolve="StableId" />
    <node concept="3EZMnI" id="1bNmcZ2iUfY" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUfZ" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUg0" role="3EZMnx">
        <property role="3F0ifm" value="value:" />
        <node concept="pVoyu" id="1bNmcZ2iUg1" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUg2" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsM" resolve="value" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUg3" role="3EZMnx">
        <property role="3F0ifm" value="namespace:" />
        <node concept="pVoyu" id="1bNmcZ2iUg4" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUg5" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsN" resolve="namespace" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUg8">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="3EZMnI" id="1bNmcZ2iUga" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUgb" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUgc" role="3EZMnx">
        <property role="3F0ifm" value="lifecycleState:" />
        <node concept="pVoyu" id="1bNmcZ2iUgd" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2iUge" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsK" resolve="lifecycleState" />
        <node concept="1sVBvm" id="1bNmcZ2jDoQ" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2jDoS" role="2wV5jI">
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUgp" role="3EZMnx">
        <property role="3F0ifm" value="authorityClass:" />
        <node concept="pVoyu" id="1bNmcZ2iUgq" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2iUgr" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsL" resolve="authorityClass" />
        <node concept="1sVBvm" id="1bNmcZ2jHmJ" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2jHmL" role="2wV5jI">
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
          </node>
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUgA" role="3EZMnx">
        <property role="3F0ifm" value="identifier:" />
        <node concept="pVoyu" id="1bNmcZ2iUgB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2iUgC" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsG" resolve="identifier" />
        <node concept="pVoyu" id="1bNmcZ2iUgD" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2iUgE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUgF" role="3EZMnx">
        <property role="3F0ifm" value="version:" />
        <node concept="pVoyu" id="1bNmcZ2iUgG" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F1sOY" id="1bNmcZ2iUgH" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsH" resolve="version" />
        <node concept="pVoyu" id="1bNmcZ2iUgI" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2iUgJ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUgK" role="3EZMnx">
        <property role="3F0ifm" value="aliases:" />
        <node concept="pVoyu" id="1bNmcZ2iUgL" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2iUgM" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsI" resolve="aliases" />
        <node concept="pVoyu" id="1bNmcZ2iUgO" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2iUgP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2iUgQ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2iUgR" role="2czzBx" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUgT" role="3EZMnx">
        <property role="3F0ifm" value="provenance:" />
        <node concept="pVoyu" id="1bNmcZ2iUgU" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2iUgV" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsJ" resolve="provenance" />
        <node concept="pVoyu" id="1bNmcZ2iUgX" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2iUgY" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2iUgZ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2iUh0" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUh4">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsx" resolve="Alias" />
    <node concept="3EZMnI" id="1bNmcZ2iUh6" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUh7" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUh8" role="3EZMnx">
        <property role="3F0ifm" value="value:" />
        <node concept="pVoyu" id="1bNmcZ2iUh9" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUha" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsO" resolve="value" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUhb" role="3EZMnx">
        <property role="3F0ifm" value="scheme:" />
        <node concept="pVoyu" id="1bNmcZ2iUhc" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhd" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsP" resolve="scheme" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUhe" role="3EZMnx">
        <property role="3F0ifm" value="retired:" />
        <node concept="pVoyu" id="1bNmcZ2iUhf" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhg" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEtH" resolve="retired" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUhj">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsy" resolve="Version" />
    <node concept="3EZMnI" id="1bNmcZ2iUhl" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUhm" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUhn" role="3EZMnx">
        <property role="3F0ifm" value="value:" />
        <node concept="pVoyu" id="1bNmcZ2iUho" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhp" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsR" resolve="value" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUhq" role="3EZMnx">
        <property role="3F0ifm" value="effectiveDate:" />
        <node concept="pVoyu" id="1bNmcZ2iUhr" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhs" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUht" role="3EZMnx">
        <property role="3F0ifm" value="supersededDate:" />
        <node concept="pVoyu" id="1bNmcZ2iUhu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhv" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUhy">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsz" resolve="LifecycleState" />
    <node concept="3EZMnI" id="1bNmcZ2iUh$" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUh_" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUhA" role="3EZMnx">
        <property role="3F0ifm" value="state:" />
        <node concept="pVoyu" id="1bNmcZ2iUhB" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhC" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsU" resolve="state" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUhD" role="3EZMnx">
        <property role="3F0ifm" value="ordinal:" />
        <node concept="pVoyu" id="1bNmcZ2iUhE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhF" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsV" resolve="ordinal" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUhG" role="3EZMnx">
        <property role="3F0ifm" value="terminal:" />
        <node concept="pVoyu" id="1bNmcZ2iUhH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhI" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsW" resolve="terminal" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUhL">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEs$" resolve="AuthorityClass" />
    <node concept="3EZMnI" id="1bNmcZ2iUhN" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUhO" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUhP" role="3EZMnx">
        <property role="3F0ifm" value="authority:" />
        <node concept="pVoyu" id="1bNmcZ2iUhQ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhR" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsX" resolve="authority" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUhS" role="3EZMnx">
        <property role="3F0ifm" value="rank:" />
        <node concept="pVoyu" id="1bNmcZ2iUhT" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhU" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsY" resolve="rank" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUhV" role="3EZMnx">
        <property role="3F0ifm" value="description:" />
        <node concept="pVoyu" id="1bNmcZ2iUhW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUhX" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEsZ" resolve="description" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUi0">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEs_" resolve="PhysicalQuantity" />
    <node concept="3EZMnI" id="1bNmcZ2iUi2" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUi3" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUi4" role="3EZMnx">
        <property role="3F0ifm" value="magnitude:" />
        <node concept="pVoyu" id="1bNmcZ2iUi5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUi6" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt0" resolve="magnitude" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUi7" role="3EZMnx">
        <property role="3F0ifm" value="doseBasis:" />
        <node concept="pVoyu" id="1bNmcZ2iUi8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUi9" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt1" resolve="doseBasis" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUia" role="3EZMnx">
        <property role="3F0ifm" value="unit:" />
        <node concept="pVoyu" id="1bNmcZ2iUib" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="1iCGBv" id="1bNmcZ2iUic" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt2" resolve="unit" />
        <node concept="1sVBvm" id="1bNmcZ2jHmO" role="1sWHZn">
          <node concept="3F0A7n" id="1bNmcZ2jHmQ" role="2wV5jI">
            <ref role="1NtTu8" to="5q6:1bNmcZ2iEt3" resolve="symbol" />
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUip">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsA" resolve="Unit" />
    <node concept="3EZMnI" id="1bNmcZ2iUir" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUis" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUit" role="3EZMnx">
        <property role="3F0ifm" value="symbol:" />
        <node concept="pVoyu" id="1bNmcZ2iUiu" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUiv" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt3" resolve="symbol" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUiw" role="3EZMnx">
        <property role="3F0ifm" value="dimension:" />
        <node concept="pVoyu" id="1bNmcZ2iUix" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUiy" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt4" resolve="dimension" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUiz" role="3EZMnx">
        <property role="3F0ifm" value="doseBasis:" />
        <node concept="pVoyu" id="1bNmcZ2iUi$" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUi_" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt5" resolve="doseBasis" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUiC">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsB" resolve="ProvenanceRef" />
    <node concept="3EZMnI" id="1bNmcZ2iUiE" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUiF" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUiG" role="3EZMnx">
        <property role="3F0ifm" value="sourcePath:" />
        <node concept="pVoyu" id="1bNmcZ2iUiH" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUiI" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt6" resolve="sourcePath" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUiJ" role="3EZMnx">
        <property role="3F0ifm" value="sourceLine:" />
        <node concept="pVoyu" id="1bNmcZ2iUiK" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUiL" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt7" resolve="sourceLine" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUiM" role="3EZMnx">
        <property role="3F0ifm" value="sha256:" />
        <node concept="pVoyu" id="1bNmcZ2iUiN" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUiO" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt8" resolve="sha256" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUiR">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsC" resolve="ExternalReference" />
    <node concept="3EZMnI" id="1bNmcZ2iUiT" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUiU" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUiV" role="3EZMnx">
        <property role="3F0ifm" value="title:" />
        <node concept="pVoyu" id="1bNmcZ2iUiW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUiX" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEt9" resolve="title" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUiY" role="3EZMnx">
        <property role="3F0ifm" value="locator:" />
        <node concept="pVoyu" id="1bNmcZ2iUiZ" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUj0" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEta" resolve="locator" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUj1" role="3EZMnx">
        <property role="3F0ifm" value="edition:" />
        <node concept="pVoyu" id="1bNmcZ2iUj2" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUj3" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEtb" resolve="edition" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUj4" role="3EZMnx">
        <property role="3F0ifm" value="retrievedDate:" />
        <node concept="pVoyu" id="1bNmcZ2iUj5" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUj6" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUj7" role="3EZMnx">
        <property role="3F0ifm" value="integrityValue:" />
        <node concept="pVoyu" id="1bNmcZ2iUj8" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUj9" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEtd" resolve="integrityValue" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUjc">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsD" resolve="AuthorityVocabulary" />
    <node concept="3EZMnI" id="1bNmcZ2iUje" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUjf" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUjg" role="3EZMnx">
        <property role="3F0ifm" value="Name:" />
        <node concept="pVoyu" id="1bNmcZ2iUjh" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUji" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEte" resolve="name" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUjj" role="3EZMnx">
        <property role="3F0ifm" value="classes:" />
        <node concept="pVoyu" id="1bNmcZ2iUjk" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2iUjl" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEtf" resolve="classes" />
        <node concept="pVoyu" id="1bNmcZ2iUjn" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2iUjo" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2iUjp" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2iUjq" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUju">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsE" resolve="UnitCatalog" />
    <node concept="3EZMnI" id="1bNmcZ2iUjw" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUjx" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUjy" role="3EZMnx">
        <property role="3F0ifm" value="Name:" />
        <node concept="pVoyu" id="1bNmcZ2iUjz" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUj$" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEtg" resolve="name" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUj_" role="3EZMnx">
        <property role="3F0ifm" value="units:" />
        <node concept="pVoyu" id="1bNmcZ2iUjA" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2iUjB" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEth" resolve="units" />
        <node concept="pVoyu" id="1bNmcZ2iUjD" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2iUjE" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2iUjF" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2iUjG" role="2czzBx" />
      </node>
    </node>
  </node>
  <node concept="24kQdi" id="1bNmcZ2iUjK">
    <ref role="1XX52x" to="5q6:1bNmcZ2iEsF" resolve="LifecycleVocabulary" />
    <node concept="3EZMnI" id="1bNmcZ2iUjM" role="2wV5jI">
      <node concept="l2Vlx" id="1bNmcZ2iUjN" role="2iSdaV" />
      <node concept="3F0ifn" id="1bNmcZ2iUjO" role="3EZMnx">
        <property role="3F0ifm" value="Name:" />
        <node concept="pVoyu" id="1bNmcZ2iUjP" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F0A7n" id="1bNmcZ2iUjQ" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEti" resolve="name" />
      </node>
      <node concept="3F0ifn" id="1bNmcZ2iUjR" role="3EZMnx">
        <property role="3F0ifm" value="states:" />
        <node concept="pVoyu" id="1bNmcZ2iUjS" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
      </node>
      <node concept="3F2HdR" id="1bNmcZ2iUjT" role="3EZMnx">
        <ref role="1NtTu8" to="5q6:1bNmcZ2iEtj" resolve="states" />
        <node concept="pVoyu" id="1bNmcZ2iUjV" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="lj46D" id="1bNmcZ2iUjW" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="pj6Ft" id="1bNmcZ2iUjX" role="3F10Kt">
          <property role="VOm3f" value="true" />
        </node>
        <node concept="l2Vlx" id="1bNmcZ2iUjY" role="2czzBx" />
      </node>
    </node>
  </node>
</model>

