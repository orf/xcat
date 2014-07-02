<?xml version="1.0" encoding="UTF-8"?>
<scm:schema xmlns:scm="http://ns.saxonica.com/schema-component-model"
            generatedAt="2010-10-19T18:15:26.281+01:00"
            xsdVersion="1.1">
   <scm:simpleType id="C0" name="explicitTimezoneType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#NCName"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="optional"/>
      <scm:enumeration value="prohibited"/>
      <scm:enumeration value="required"/>
   </scm:simpleType>
   <scm:simpleType id="C1" base="#NCName" variety="atomic" primitiveType="#string">
      <scm:enumeration value="preserve"/>
      <scm:enumeration value="default"/>
   </scm:simpleType>
   <scm:simpleType id="C2" name="builtInTypeReferenceType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#string"
                   variety="atomic"
                   primitiveType="#string">
      <scm:pattern value="#[a-zA-Z0-9]+"/>
   </scm:simpleType>
   <scm:simpleType id="C3" name="namespaceListType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="list"
                   itemType="C4"/>
   <scm:simpleType id="C5" name="finalType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="list"
                   itemType="C6"/>
   <scm:complexType id="C7" name="xpathContainerType"
                    targetNamespace="http://ns.saxonica.com/schema-component-model"
                    base="#anyType"
                    derivationMethod="restriction"
                    abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C8"/>
      <scm:attributeUse required="true" ref="C9"/>
      <scm:attributeUse required="false" ref="C10"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:simpleType id="C11" name="whitespaceType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#NCName"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="collapse"/>
      <scm:enumeration value="replace"/>
      <scm:enumeration value="preserve"/>
   </scm:simpleType>
   <scm:simpleType id="C6" name="derivationMethodType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#NCName"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="union"/>
      <scm:enumeration value="list"/>
      <scm:enumeration value="substitution"/>
      <scm:enumeration value="restriction"/>
      <scm:enumeration value="extension"/>
   </scm:simpleType>
   <scm:simpleType id="C12" base="#anySimpleType" variety="union" memberTypes="#language C13"/>
   <scm:simpleType id="C14" name="complexVarietyType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#NCName"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="element-only"/>
      <scm:enumeration value="mixed"/>
      <scm:enumeration value="simple"/>
      <scm:enumeration value="empty"/>
   </scm:simpleType>
   <scm:simpleType id="C15" name="typeReferenceType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="union"
                   memberTypes="C2 #IDREF"/>
   <scm:simpleType id="C16" name="pseudoNamespaceType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#string"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="##targetNamespace"/>
      <scm:enumeration value="##other"/>
      <scm:enumeration value="##local"/>
      <scm:enumeration value="##defaultNamespace"/>
      <scm:enumeration value="##absent"/>
      <scm:enumeration value="##any"/>
   </scm:simpleType>
   <scm:simpleType id="C17" name="notQNameListType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="list"
                   itemType="C18"/>
   <scm:simpleType id="C13" base="#string" variety="atomic" primitiveType="#string">
      <scm:enumeration value=""/>
   </scm:simpleType>
   <scm:complexType id="C19" name="identityConstraintType"
                    targetNamespace="http://ns.saxonica.com/schema-component-model"
                    base="#anyType"
                    derivationMethod="restriction"
                    abstract="false"
                    variety="element-only">
      <scm:attributeUse required="true" ref="C20"/>
      <scm:attributeUse required="true" ref="C21"/>
      <scm:attributeUse required="false" ref="C22"/>
      <scm:attributeUse required="false" ref="C23"/>
      <scm:modelGroupParticle minOccurs="1" maxOccurs="1">
         <scm:sequence>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C24"/>
            <scm:elementParticle minOccurs="1" maxOccurs="unbounded" ref="C25"/>
         </scm:sequence>
      </scm:modelGroupParticle>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0">
            <scm:edge term="C24" to="1"/>
         </scm:state>
         <scm:state nr="1">
            <scm:edge term="C25" to="2"/>
         </scm:state>
         <scm:state nr="2" final="true">
            <scm:edge term="C25" to="3"/>
         </scm:state>
         <scm:state nr="3" final="true">
            <scm:edge term="C25" to="3"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:simpleType id="C26" name="xpathExpressionType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#string"
                   variety="atomic"
                   primitiveType="#string">
      <scm:pattern value=".+"/>
   </scm:simpleType>
   <scm:complexType id="C27" name="abstractParticleType"
                    targetNamespace="http://ns.saxonica.com/schema-component-model"
                    base="#anyType"
                    derivationMethod="restriction"
                    abstract="true"
                    variety="empty">
      <scm:attributeUse required="true" ref="C28"/>
      <scm:attributeUse required="true" ref="C29"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:simpleType id="C4" name="namespaceType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="union"
                   memberTypes="C16 C30"/>
   <scm:simpleType id="C30" name="uriType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#token"
                   variety="atomic"
                   primitiveType="#string">
      <scm:pattern value="[^\s\r\n\t]*"/>
   </scm:simpleType>
   <scm:simpleType id="C18" name="notQNameType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="union"
                   memberTypes="C31 C32 #NCName"/>
   <scm:complexType id="C33" name="typedValueType"
                    targetNamespace="http://ns.saxonica.com/schema-component-model"
                    base="#anyType"
                    derivationMethod="restriction"
                    abstract="false"
                    variety="element-only">
      <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C34"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C34" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C34" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:simpleType id="C35" name="processContentsType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#NCName"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="skip"/>
      <scm:enumeration value="lax"/>
      <scm:enumeration value="strict"/>
   </scm:simpleType>
   <scm:simpleType id="C36" name="unboundedType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#NCName"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="unbounded"/>
   </scm:simpleType>
   <scm:simpleType id="C31" name="pseudoQNameType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#string"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="##definedSibling"/>
      <scm:enumeration value="##defined"/>
   </scm:simpleType>
   <scm:simpleType id="C37" name="xsdVersionType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#string"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="1.1"/>
      <scm:enumeration value="1.0"/>
   </scm:simpleType>
   <scm:simpleType id="C32" name="clarkNameType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#string"
                   variety="atomic"
                   primitiveType="#string">
      <scm:pattern value="\{[^{}]*\}\i\c*"/>
   </scm:simpleType>
   <scm:simpleType id="C38" name="maxOccursType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="union"
                   memberTypes="#nonNegativeInteger C36"/>
   <scm:simpleType id="C39" name="openContentModeType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#NCName"
                   variety="atomic"
                   primitiveType="#string">
      <scm:enumeration value="interleave"/>
      <scm:enumeration value="suffix"/>
   </scm:simpleType>
   <scm:simpleType id="C40" name="blockType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="list"
                   itemType="C6"/>
   <scm:simpleType id="C41" name="typeReferenceListType"
                   targetNamespace="http://ns.saxonica.com/schema-component-model"
                   base="#anySimpleType"
                   variety="list"
                   itemType="C15"/>
   <scm:element id="C42" name="totalDigits"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C43"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C45" name="enumeration"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C46"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C47" name="attributeWildcard"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C48"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C49" name="simpleType"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C50"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C51" name="maxInclusive"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C52"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C53" name="minLength"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C54"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C55" name="maxLength"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C56"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C57" name="substitutionGroupAffiliation"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C58"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C59" name="assertion"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C60"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C61" name="openContent"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C62"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C63" name="modelGroupDefinition"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C64"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C65" name="attributeGroup"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C66"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C44" name="abstractFacet"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="#anyType"
                global="true"
                nillable="false"
                abstract="true"/>
   <scm:element id="C67" name="modelGroupParticle"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C68"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C69"/>
   </scm:element>
   <scm:element id="C70" name="element"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C71"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C72" name="elementParticle"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C73"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C69"/>
   </scm:element>
   <scm:element id="C74" name="pattern"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C75"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C76" name="explicitTimezone"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C77"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C78" name="notation"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C79"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C80" name="minInclusive"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C81"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C82" name="schema"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C83"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C84" name="length"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C85"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C86" name="maxScale"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C87"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C88" name="abstractModelGroup"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C89"
                global="true"
                nillable="false"
                abstract="true"/>
   <scm:element id="C25" name="field"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C7"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C90" name="wildcard"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C91"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C69" name="abstractParticle"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C27"
                global="true"
                nillable="false"
                abstract="true"/>
   <scm:element id="C92" name="assert"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C93"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C94" name="state"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C95"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C96" name="unique"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C19"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C97" name="attributeUse"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C98"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C99" name="sequence"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C89"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C88"/>
   </scm:element>
   <scm:element id="C100" name="choice"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C89"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C88"/>
   </scm:element>
   <scm:element id="C101" name="key"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C19"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C102" name="all"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C89"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C88"/>
   </scm:element>
   <scm:element id="C103" name="attribute"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C104"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C105" name="maxExclusive"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C106"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C107" name="minExclusive"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C108"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C109" name="edge"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C110"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C24" name="selector"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C7"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C111" name="keyref"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C19"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C112" name="fixed"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C33"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C113" name="complexType"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C114"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C115" name="minScale"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C116"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C117" name="preprocess"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C118"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C119" name="alternativeType"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C120"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C121" name="elementWildcard"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C122"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C69"/>
   </scm:element>
   <scm:element id="C123" name="fractionDigits"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C124"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C125" name="identityConstraint"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C126"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:element id="C127" name="whiteSpace"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C128"
                global="true"
                nillable="false"
                abstract="false">
      <scm:substitutionGroupAffiliation ref="C44"/>
   </scm:element>
   <scm:element id="C129" name="finiteStateMachine"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C130"
                global="true"
                nillable="false"
                abstract="false"/>
   <scm:attribute id="C131" name="lang" targetNamespace="http://www.w3.org/XML/1998/namespace"
                  type="C12"
                  global="true"/>
   <scm:attribute id="C132" name="space" targetNamespace="http://www.w3.org/XML/1998/namespace"
                  type="C1"
                  global="true"/>
   <scm:attribute id="C133" name="id" targetNamespace="http://www.w3.org/XML/1998/namespace"
                  type="#ID"
                  global="true"/>
   <scm:attribute id="C10" name="base" targetNamespace="http://www.w3.org/XML/1998/namespace"
                  type="#anyURI"
                  global="true"/>
   <scm:attributeGroup id="C134" name="specialAttrs"
                       targetNamespace="http://www.w3.org/XML/1998/namespace">
      <scm:attributeUse required="false" ref="C10"/>
      <scm:attributeUse required="false" ref="C131"/>
      <scm:attributeUse required="false" ref="C132"/>
      <scm:attributeUse required="false" ref="C133"/>
   </scm:attributeGroup>
   <scm:complexType id="C89" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:modelGroupParticle minOccurs="0" maxOccurs="unbounded">
         <scm:sequence>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C69"/>
         </scm:sequence>
      </scm:modelGroupParticle>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C121" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C121" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C71" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="true" ref="C135"/>
      <scm:attributeUse required="false" ref="C136"/>
      <scm:attributeUse required="false" ref="C137"/>
      <scm:attributeUse required="false" ref="C138"/>
      <scm:attributeUse required="false" ref="C139"/>
      <scm:attributeUse required="true" ref="C140"/>
      <scm:attributeUse required="true" ref="C141"/>
      <scm:attributeUse required="true" ref="C142"/>
      <scm:attributeUse required="true" ref="C143"/>
      <scm:attributeUse required="false" ref="C144"/>
      <scm:attributeUse required="true" ref="C145"/>
      <scm:modelGroupParticle minOccurs="1" maxOccurs="1">
         <scm:sequence>
            <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C57"/>
            <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C119"/>
            <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C125"/>
            <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C112"/>
         </scm:sequence>
      </scm:modelGroupParticle>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C112" to="1"/>
            <scm:edge term="C57" to="2"/>
            <scm:edge term="C125" to="3"/>
            <scm:edge term="C119" to="4"/>
         </scm:state>
         <scm:state nr="1" final="true"/>
         <scm:state nr="2" final="true">
            <scm:edge term="C112" to="1"/>
            <scm:edge term="C57" to="2"/>
            <scm:edge term="C125" to="3"/>
            <scm:edge term="C119" to="4"/>
         </scm:state>
         <scm:state nr="3" final="true">
            <scm:edge term="C112" to="1"/>
            <scm:edge term="C125" to="3"/>
         </scm:state>
         <scm:state nr="4" final="true">
            <scm:edge term="C112" to="1"/>
            <scm:edge term="C125" to="3"/>
            <scm:edge term="C119" to="4"/>
         </scm:state>
      </scm:finiteStateMachine>
      <scm:assertion xmlns:xs="http://www.w3.org/2001/XMLSchema"
                     xmlns:vc="http://www.w3.org/2007/XMLSchema-versioning"
                     test="not(@default and scm:fixed)"
                     defaultNamespace=""
                     xml:base="file:/c:/MyJava/samples/scm/scmschema.xsd"/>
   </scm:complexType>
   <scm:attribute id="C28" name="maxOccurs" type="C38" global="false" containingComplexType="C27"/>
   <scm:complexType id="C116" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C146"/>
      <scm:attributeUse required="false" ref="C147" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C9" name="defaultNamespace" type="C30" global="false"
                  containingComplexType="C7"/>
   <scm:complexType id="C110" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C148"/>
      <scm:attributeUse required="true" ref="C149"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C66" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="true" ref="C150"/>
      <scm:attributeUse required="false" ref="C151"/>
      <scm:attributeUse required="false" ref="C152"/>
      <scm:modelGroupParticle minOccurs="1" maxOccurs="1">
         <scm:sequence>
            <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C97"/>
            <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C47"/>
         </scm:sequence>
      </scm:modelGroupParticle>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C97" to="1"/>
            <scm:edge term="C47" to="2"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C97" to="1"/>
            <scm:edge term="C47" to="2"/>
         </scm:state>
         <scm:state nr="2" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C118" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="false" ref="C153" default="false"/>
      <scm:elementParticle minOccurs="1" maxOccurs="2" ref="C59"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0">
            <scm:edge term="C59" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true" minOccurs="1" maxOccurs="2">
            <scm:edge term="C59" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C153" name="fixed" type="#boolean" global="false"
                  containingComplexType="C118"/>
   <scm:complexType id="C62" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="false" ref="C154"/>
      <scm:attributeUse required="false" ref="C155"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C46" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C156"/>
      <scm:attributeUse required="false" ref="C157" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C156" name="value" type="#anySimpleType" global="false"
                  containingComplexType="C46"/>
   <scm:attribute id="C148" name="term" type="#IDREF" global="false" containingComplexType="C110"/>
   <scm:attribute id="C147" name="fixed" type="#boolean" global="false"
                  containingComplexType="C116"/>
   <scm:complexType id="C104" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="false" ref="C158"/>
      <scm:attributeUse required="false" ref="C159"/>
      <scm:attributeUse required="true" ref="C160"/>
      <scm:attributeUse required="true" ref="C161"/>
      <scm:attributeUse required="true" ref="C162"/>
      <scm:attributeUse required="false" ref="C163"/>
      <scm:attributeUse required="true" ref="C164"/>
      <scm:attributeUse required="true" ref="C165"/>
      <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C112"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C112" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C159" name="default" type="#string" global="false"
                  containingComplexType="C104"/>
   <scm:attribute id="C160" name="global" type="#boolean" global="false"
                  containingComplexType="C104"/>
   <scm:complexType id="C52" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C166"/>
      <scm:attributeUse required="false" ref="C167" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C166" name="value" type="#anySimpleType" global="false"
                  containingComplexType="C52"/>
   <scm:attribute id="C155" name="wildcard" type="#IDREF" global="false"
                  containingComplexType="C62"/>
   <scm:attribute id="C152" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C66"/>
   <scm:attribute id="C150" name="id" type="#ID" global="false" containingComplexType="C66"/>
   <scm:complexType id="C60" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C168"/>
      <scm:attributeUse required="true" ref="C169"/>
      <scm:attributeUse required="false" ref="C10"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C64" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="true" ref="C170"/>
      <scm:attributeUse required="false" ref="C171"/>
      <scm:attributeUse required="false" ref="C172"/>
      <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C69"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C121" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C121" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C136" name="block" type="C40" global="false" containingComplexType="C71"/>
   <scm:attribute id="C21" name="name" type="#NCName" global="false" containingComplexType="C19"/>
   <scm:complexType id="C68" base="C27" derivationMethod="extension" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="false" ref="C173"/>
      <scm:attributeUse required="true" ref="C28"/>
      <scm:attributeUse required="true" ref="C29"/>
      <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C88"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C102" to="1"/>
            <scm:edge term="C100" to="1"/>
            <scm:edge term="C88" to="1"/>
            <scm:edge term="C99" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C102" to="1"/>
            <scm:edge term="C100" to="1"/>
            <scm:edge term="C88" to="1"/>
            <scm:edge term="C99" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C98" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="false" ref="C174"/>
      <scm:attributeUse required="true" ref="C175"/>
      <scm:attributeUse required="true" ref="C176"/>
      <scm:attributeUse required="true" ref="C177"/>
      <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C112"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C112" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C174" name="default" type="#string" global="false"
                  containingComplexType="C98"/>
   <scm:attribute id="C175" name="ref" type="#IDREF" global="false" containingComplexType="C98"/>
   <scm:complexType id="C79" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C178"/>
      <scm:attributeUse required="false" ref="C179"/>
      <scm:attributeUse required="false" ref="C180"/>
      <scm:attributeUse required="false" ref="C181"/>
      <scm:attributeUse required="false" ref="C182"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C182" name="publicId" type="#string" global="false"
                  containingComplexType="C79"/>
   <scm:attribute id="C179" name="name" type="#NCName" global="false" containingComplexType="C79"/>
   <scm:attribute id="C180" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C79"/>
   <scm:attribute id="C173" name="ref" type="#IDREF" global="false" containingComplexType="C68"/>
   <scm:complexType id="C54" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C183"/>
      <scm:attributeUse required="false" ref="C184" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C172" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C64"/>
   <scm:attribute id="C149" name="to" type="#integer" global="false" containingComplexType="C110"/>
   <scm:attribute id="C139" name="final" type="C5" global="false" containingComplexType="C71"/>
   <scm:complexType id="C43" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C185"/>
      <scm:attributeUse required="false" ref="C186" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C185" name="value" type="#positiveInteger" global="false"
                  containingComplexType="C43"/>
   <scm:complexType id="C124" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C187"/>
      <scm:attributeUse required="false" ref="C188" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C187" name="value" type="#nonNegativeInteger" global="false"
                  containingComplexType="C124"/>
   <scm:attribute id="C188" name="fixed" type="#boolean" global="false"
                  containingComplexType="C124"/>
   <scm:attribute id="C157" name="namespaceSensitive" type="#boolean" global="false"
                  containingComplexType="C46"/>
   <scm:attribute id="C144" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C71"/>
   <scm:attribute id="C171" name="name" type="#NCName" global="false" containingComplexType="C64"/>
   <scm:attribute id="C143" name="nillable" type="#boolean" global="false"
                  containingComplexType="C71"/>
   <scm:attribute id="C169" name="defaultNamespace" type="C30" global="false"
                  containingComplexType="C60"/>
   <scm:attribute id="C158" name="containingComplexType" type="#IDREF" global="false"
                  containingComplexType="C104"/>
   <scm:complexType id="C50" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="true" ref="C189"/>
      <scm:attributeUse required="false" ref="C190"/>
      <scm:attributeUse required="true" ref="C191"/>
      <scm:attributeUse required="false" ref="C192"/>
      <scm:attributeUse required="false" ref="C193"/>
      <scm:attributeUse required="false" ref="C194"/>
      <scm:attributeUse required="false" ref="C195"/>
      <scm:attributeUse required="false" ref="C196"/>
      <scm:attributeUse required="true" ref="C197"/>
      <scm:modelGroupParticle minOccurs="0" maxOccurs="unbounded">
         <scm:sequence>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C44"/>
         </scm:sequence>
      </scm:modelGroupParticle>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C42" to="1"/>
            <scm:edge term="C45" to="1"/>
            <scm:edge term="C51" to="1"/>
            <scm:edge term="C53" to="1"/>
            <scm:edge term="C55" to="1"/>
            <scm:edge term="C44" to="1"/>
            <scm:edge term="C74" to="1"/>
            <scm:edge term="C76" to="1"/>
            <scm:edge term="C80" to="1"/>
            <scm:edge term="C84" to="1"/>
            <scm:edge term="C86" to="1"/>
            <scm:edge term="C92" to="1"/>
            <scm:edge term="C107" to="1"/>
            <scm:edge term="C105" to="1"/>
            <scm:edge term="C115" to="1"/>
            <scm:edge term="C117" to="1"/>
            <scm:edge term="C123" to="1"/>
            <scm:edge term="C127" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C42" to="1"/>
            <scm:edge term="C45" to="1"/>
            <scm:edge term="C51" to="1"/>
            <scm:edge term="C53" to="1"/>
            <scm:edge term="C55" to="1"/>
            <scm:edge term="C44" to="1"/>
            <scm:edge term="C74" to="1"/>
            <scm:edge term="C76" to="1"/>
            <scm:edge term="C80" to="1"/>
            <scm:edge term="C84" to="1"/>
            <scm:edge term="C86" to="1"/>
            <scm:edge term="C92" to="1"/>
            <scm:edge term="C107" to="1"/>
            <scm:edge term="C105" to="1"/>
            <scm:edge term="C115" to="1"/>
            <scm:edge term="C117" to="1"/>
            <scm:edge term="C123" to="1"/>
            <scm:edge term="C127" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C189" name="base" type="C15" global="false" containingComplexType="C50"/>
   <scm:attribute id="C190" name="final" type="C5" global="false" containingComplexType="C50"/>
   <scm:attribute id="C194" name="name" type="#NCName" global="false" containingComplexType="C50"/>
   <scm:attribute id="C191" name="id" type="#ID" global="false" containingComplexType="C50"/>
   <scm:attribute id="C197" name="variety" type="#NCName" global="false"
                  containingComplexType="C50"/>
   <scm:attribute id="C29" name="minOccurs" type="#nonNegativeInteger" global="false"
                  containingComplexType="C27"/>
   <scm:complexType id="C91" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C198"/>
      <scm:attributeUse required="true" ref="C199"/>
      <scm:attributeUse required="false" ref="C200"/>
      <scm:attributeUse required="true" ref="C201"/>
      <scm:attributeUse required="false" ref="C202"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C198" name="constraint" type="#NCName" global="false"
                  containingComplexType="C91"/>
   <scm:attribute id="C201" name="processContents" type="C35" global="false"
                  containingComplexType="C91"/>
   <scm:attribute id="C199" name="id" type="#ID" global="false" containingComplexType="C91"/>
   <scm:attribute id="C200" name="namespaces" type="C3" global="false"
                  containingComplexType="C91"/>
   <scm:complexType id="C106" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C203"/>
      <scm:attributeUse required="false" ref="C204" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C203" name="value" type="#anySimpleType" global="false"
                  containingComplexType="C106"/>
   <scm:complexType id="C126" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C205"/>
      <scm:attributeUse required="false" ref="C10"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C205" name="ref" type="#IDREF" global="false" containingComplexType="C126"/>
   <scm:complexType id="C56" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C206"/>
      <scm:attributeUse required="false" ref="C207" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C206" name="value" type="#nonNegativeInteger" global="false"
                  containingComplexType="C56"/>
   <scm:attribute id="C184" name="fixed" type="#boolean" global="false"
                  containingComplexType="C54"/>
   <scm:attribute id="C8" name="xpath" type="C26" global="false" containingComplexType="C7"/>
   <scm:complexType id="C114" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="true" ref="C208"/>
      <scm:attributeUse required="true" ref="C209"/>
      <scm:attributeUse required="true" ref="C210"/>
      <scm:attributeUse required="false" ref="C211"/>
      <scm:attributeUse required="false" ref="C212"/>
      <scm:attributeUse required="true" ref="C213"/>
      <scm:attributeUse required="false" ref="C214"/>
      <scm:attributeUse required="false" ref="C215"/>
      <scm:attributeUse required="false" ref="C216"/>
      <scm:attributeUse required="true" ref="C217"/>
      <scm:modelGroupParticle minOccurs="1" maxOccurs="1">
         <scm:sequence>
            <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C61"/>
            <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C97"/>
            <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C47"/>
            <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C69"/>
            <scm:elementParticle minOccurs="0" maxOccurs="1" ref="C129"/>
            <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C59"/>
         </scm:sequence>
      </scm:modelGroupParticle>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C47" to="4"/>
            <scm:edge term="C59" to="2"/>
            <scm:edge term="C61" to="5"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C97" to="3"/>
            <scm:edge term="C121" to="1"/>
            <scm:edge term="C129" to="6"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C59" to="2"/>
            <scm:edge term="C129" to="6"/>
         </scm:state>
         <scm:state nr="2" final="true">
            <scm:edge term="C59" to="2"/>
         </scm:state>
         <scm:state nr="3" final="true">
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C59" to="2"/>
            <scm:edge term="C97" to="3"/>
            <scm:edge term="C47" to="4"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C121" to="1"/>
            <scm:edge term="C129" to="6"/>
         </scm:state>
         <scm:state nr="4" final="true">
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C59" to="2"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C121" to="1"/>
            <scm:edge term="C129" to="6"/>
         </scm:state>
         <scm:state nr="5" final="true">
            <scm:edge term="C69" to="1"/>
            <scm:edge term="C59" to="2"/>
            <scm:edge term="C97" to="3"/>
            <scm:edge term="C47" to="4"/>
            <scm:edge term="C72" to="1"/>
            <scm:edge term="C67" to="1"/>
            <scm:edge term="C121" to="1"/>
            <scm:edge term="C129" to="6"/>
         </scm:state>
         <scm:state nr="6" final="true">
            <scm:edge term="C59" to="2"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C217" name="variety" type="C14" global="false" containingComplexType="C114"/>
   <scm:attribute id="C215" name="simpleType" type="C15" global="false"
                  containingComplexType="C114"/>
   <scm:attribute id="C208" name="abstract" type="#boolean" global="false"
                  containingComplexType="C114"/>
   <scm:attribute id="C209" name="base" type="C15" global="false" containingComplexType="C114"/>
   <scm:attribute id="C213" name="id" type="#ID" global="false" containingComplexType="C114"/>
   <scm:complexType id="C85" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C218"/>
      <scm:attributeUse required="false" ref="C219" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C219" name="fixed" type="#boolean" global="false"
                  containingComplexType="C85"/>
   <scm:attribute id="C204" name="fixed" type="#boolean" global="false"
                  containingComplexType="C106"/>
   <scm:attribute id="C167" name="fixed" type="#boolean" global="false"
                  containingComplexType="C52"/>
   <scm:attribute id="C137" name="containingComplexType" type="#IDREF" global="false"
                  containingComplexType="C71"/>
   <scm:attribute id="C165" name="inheritable" type="#boolean" global="false"
                  containingComplexType="C104"/>
   <scm:attribute id="C176" name="required" type="#boolean" global="false"
                  containingComplexType="C98"/>
   <scm:attribute id="C212" name="final" type="C5" global="false" containingComplexType="C114"/>
   <scm:attribute id="C22" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C19"/>
   <scm:attribute id="C168" name="test" type="C26" global="false" containingComplexType="C60"/>
   <scm:complexType id="C122" base="C27" derivationMethod="extension" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C220"/>
      <scm:attributeUse required="true" ref="C28"/>
      <scm:attributeUse required="true" ref="C29"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C220" name="ref" type="#IDREF" global="false" containingComplexType="C122"/>
   <scm:attribute id="C177" name="inheritable" type="#boolean" global="false"
                  containingComplexType="C98"/>
   <scm:attribute id="C193" name="memberTypes" type="C41" global="false"
                  containingComplexType="C50"/>
   <scm:complexType id="C93" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="false" ref="C221" default="false"/>
      <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C59"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0">
            <scm:edge term="C59" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C221" name="fixed" type="#boolean" global="false"
                  containingComplexType="C93"/>
   <scm:attribute id="C135" name="abstract" type="#boolean" global="false"
                  containingComplexType="C71"/>
   <scm:attribute id="C218" name="value" type="#nonNegativeInteger" global="false"
                  containingComplexType="C85"/>
   <scm:attribute id="C195" name="primitiveType" type="C2" global="false"
                  containingComplexType="C50"/>
   <scm:complexType id="C83" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="false" ref="C222"/>
      <scm:attributeUse required="false" ref="C223"/>
      <scm:modelGroupParticle minOccurs="0" maxOccurs="unbounded">
         <scm:choice>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C70"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C103"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C113"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C49"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C65"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C63"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C78"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C90"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C96"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C101"/>
            <scm:elementParticle minOccurs="1" maxOccurs="1" ref="C111"/>
         </scm:choice>
      </scm:modelGroupParticle>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C49" to="1"/>
            <scm:edge term="C65" to="1"/>
            <scm:edge term="C63" to="1"/>
            <scm:edge term="C70" to="1"/>
            <scm:edge term="C78" to="1"/>
            <scm:edge term="C90" to="1"/>
            <scm:edge term="C96" to="1"/>
            <scm:edge term="C101" to="1"/>
            <scm:edge term="C103" to="1"/>
            <scm:edge term="C111" to="1"/>
            <scm:edge term="C113" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C49" to="1"/>
            <scm:edge term="C65" to="1"/>
            <scm:edge term="C63" to="1"/>
            <scm:edge term="C70" to="1"/>
            <scm:edge term="C78" to="1"/>
            <scm:edge term="C90" to="1"/>
            <scm:edge term="C96" to="1"/>
            <scm:edge term="C101" to="1"/>
            <scm:edge term="C103" to="1"/>
            <scm:edge term="C111" to="1"/>
            <scm:edge term="C113" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C222" name="generatedAt" type="#dateTime" global="false"
                  containingComplexType="C83"/>
   <scm:attribute id="C214" name="name" type="#NCName" global="false"
                  containingComplexType="C114"/>
   <scm:attribute id="C23" name="key" type="#IDREF" global="false" containingComplexType="C19"/>
   <scm:complexType id="C95" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="false" ref="C224"/>
      <scm:attributeUse required="false" ref="C225"/>
      <scm:attributeUse required="false" ref="C226"/>
      <scm:attributeUse required="false" ref="C227"/>
      <scm:attributeUse required="true" ref="C228"/>
      <scm:elementParticle minOccurs="0" maxOccurs="unbounded" ref="C109"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true">
            <scm:edge term="C109" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C109" to="1"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C228" name="nr" type="#integer" global="false" containingComplexType="C95"/>
   <scm:attribute id="C227" name="minOccurs" type="#integer" global="false"
                  containingComplexType="C95"/>
   <scm:attribute id="C224" name="afterMax" type="#integer" global="false"
                  containingComplexType="C95"/>
   <scm:attribute id="C225" name="final" type="#boolean" global="false"
                  containingComplexType="C95"/>
   <scm:attribute id="C223" name="xsdVersion" type="C37" global="false"
                  containingComplexType="C83"/>
   <scm:attribute id="C211" name="block" type="C40" global="false" containingComplexType="C114"/>
   <scm:attribute id="C138" name="default" type="#string" global="false"
                  containingComplexType="C71"/>
   <scm:complexType id="C130" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="element-only">
      <scm:attributeUse required="true" ref="C229"/>
      <scm:elementParticle minOccurs="1" maxOccurs="unbounded" ref="C94"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0">
            <scm:edge term="C94" to="1"/>
         </scm:state>
         <scm:state nr="1" final="true">
            <scm:edge term="C94" to="2"/>
         </scm:state>
         <scm:state nr="2" final="true">
            <scm:edge term="C94" to="2"/>
         </scm:state>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C128" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C230"/>
      <scm:attributeUse required="false" ref="C231" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C230" name="value" type="C11" global="false" containingComplexType="C128"/>
   <scm:attribute id="C210" name="derivationMethod" type="C6" global="false"
                  containingComplexType="C114"/>
   <scm:attribute id="C207" name="fixed" type="#boolean" global="false"
                  containingComplexType="C56"/>
   <scm:attribute id="C170" name="id" type="#ID" global="false" containingComplexType="C64"/>
   <scm:attribute id="C163" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C104"/>
   <scm:complexType id="C48" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C232"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C232" name="ref" type="#IDREF" global="false" containingComplexType="C48"/>
   <scm:attribute id="C202" name="notQName" type="C17" global="false" containingComplexType="C91"/>
   <scm:complexType id="C108" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C233"/>
      <scm:attributeUse required="false" ref="C234" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C233" name="value" type="#anySimpleType" global="false"
                  containingComplexType="C108"/>
   <scm:attribute id="C234" name="fixed" type="#boolean" global="false"
                  containingComplexType="C108"/>
   <scm:attribute id="C183" name="value" type="#nonNegativeInteger" global="false"
                  containingComplexType="C54"/>
   <scm:attribute id="C162" name="name" type="#NCName" global="false"
                  containingComplexType="C104"/>
   <scm:attribute id="C229" name="initialState" type="#integer" global="false"
                  containingComplexType="C130"/>
   <scm:attribute id="C145" name="type" type="C15" global="false" containingComplexType="C71"/>
   <scm:complexType id="C81" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C235"/>
      <scm:attributeUse required="false" ref="C236" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:complexType id="C73" base="C27" derivationMethod="extension" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C237"/>
      <scm:attributeUse required="true" ref="C28"/>
      <scm:attributeUse required="true" ref="C29"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C237" name="ref" type="#IDREF" global="false" containingComplexType="C73"/>
   <scm:complexType id="C75" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C238"/>
      <scm:attributeUse required="false" ref="C239" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C239" name="fixed" type="#boolean" global="false"
                  containingComplexType="C75"/>
   <scm:attribute id="C238" name="value" type="#string" global="false"
                  containingComplexType="C75"/>
   <scm:attribute id="C236" name="fixed" type="#boolean" global="false"
                  containingComplexType="C81"/>
   <scm:attribute id="C141" name="id" type="#ID" global="false" containingComplexType="C71"/>
   <scm:element id="C34" name="item"
                targetNamespace="http://ns.saxonica.com/schema-component-model"
                type="C240"
                global="false"
                containingComplexType="C33"
                nillable="false"
                abstract="false"/>
   <scm:complexType id="C240" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C241"/>
      <scm:attributeUse required="true" ref="C242"/>
      <scm:attributeUse required="false" ref="C243"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C243" name="namespace" type="C30" global="false"
                  containingComplexType="C240"/>
   <scm:attribute id="C241" name="type" type="C2" global="false" containingComplexType="C240"/>
   <scm:attribute id="C242" name="value" type="#string" global="false"
                  containingComplexType="C240"/>
   <scm:attribute id="C231" name="fixed" type="#boolean" global="false"
                  containingComplexType="C128"/>
   <scm:attribute id="C20" name="id" type="#ID" global="false" containingComplexType="C19"/>
   <scm:attribute id="C181" name="systemId" type="C30" global="false" containingComplexType="C79"/>
   <scm:complexType id="C87" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C244"/>
      <scm:attributeUse required="false" ref="C245" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C244" name="value" type="#anySimpleType" global="false"
                  containingComplexType="C87"/>
   <scm:attribute id="C245" name="fixed" type="#boolean" global="false"
                  containingComplexType="C87"/>
   <scm:attribute id="C142" name="name" type="#NCName" global="false" containingComplexType="C71"/>
   <scm:complexType id="C77" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C246"/>
      <scm:attributeUse required="false" ref="C247" default="false"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C246" name="value" type="C0" global="false" containingComplexType="C77"/>
   <scm:attribute id="C247" name="fixed" type="#boolean" global="false"
                  containingComplexType="C77"/>
   <scm:attribute id="C140" name="global" type="#boolean" global="false"
                  containingComplexType="C71"/>
   <scm:attribute id="C164" name="type" type="C15" global="false" containingComplexType="C104"/>
   <scm:attribute id="C146" name="value" type="#anySimpleType" global="false"
                  containingComplexType="C116"/>
   <scm:attribute id="C226" name="maxOccurs" type="C38" global="false"
                  containingComplexType="C95"/>
   <scm:attribute id="C192" name="itemType" type="C15" global="false" containingComplexType="C50"/>
   <scm:attribute id="C178" name="id" type="#ID" global="false" containingComplexType="C79"/>
   <scm:attribute id="C235" name="value" type="#anySimpleType" global="false"
                  containingComplexType="C81"/>
   <scm:attribute id="C161" name="id" type="#ID" global="false" containingComplexType="C104"/>
   <scm:attribute id="C154" name="mode" type="C39" global="false" containingComplexType="C62"/>
   <scm:attribute id="C151" name="name" type="#NCName" global="false" containingComplexType="C66"/>
   <scm:attribute id="C186" name="fixed" type="#boolean" global="false"
                  containingComplexType="C43"/>
   <scm:complexType id="C58" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C248"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C248" name="ref" type="#IDREF" global="false" containingComplexType="C58"/>
   <scm:complexType id="C120" base="#anyType" derivationMethod="restriction" abstract="false"
                    variety="empty">
      <scm:attributeUse required="true" ref="C249"/>
      <scm:attributeUse required="true" ref="C250"/>
      <scm:attributeUse required="true" ref="C251"/>
      <scm:attributeUse required="false" ref="C10"/>
      <scm:finiteStateMachine initialState="0">
         <scm:state nr="0" final="true"/>
      </scm:finiteStateMachine>
   </scm:complexType>
   <scm:attribute id="C249" name="type" type="C15" global="false" containingComplexType="C120"/>
   <scm:attribute id="C251" name="defaultNamespace" type="C30" global="false"
                  containingComplexType="C120"/>
   <scm:attribute id="C250" name="test" type="C26" global="false" containingComplexType="C120"/>
   <scm:attribute id="C216" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C114"/>
   <scm:attribute id="C196" name="targetNamespace" type="C30" global="false"
                  containingComplexType="C50"/>
</scm:schema>