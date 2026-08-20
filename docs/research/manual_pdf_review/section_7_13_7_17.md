# SysML 2.0 textual-example audit: printed pages 65-100

## Scope and method

Source: `/tmp/SysML-2.0-Language.pdf`, OMG Systems Modeling Language v2.0,
Part 1, formal/2026-03-02 (March 2026). The requested printed pages map to
PDF object pages 97-132 (the PDF front matter is not numbered like the body).
I rendered every page in that interval and read the page images alongside the
layout text. Printed page 101 was also inspected solely to finish the example
that starts on page 100.

The inventory has **90 rows**. A row is one complete textual example/declaration
or one textual-notation cell example in a representative-notation table. When a
single cell contains two complete alternatives or declarations, they are split
into separate rows so each row remains independently reusable. Repeated textual
cells are retained as separate rows when the specification presents them as
separate cells (for example, the two `actionWithLoop1` cells on pages 93 and
94). Whitespace and PDF line wrapping are normalized; tokens, comments,
punctuation, names, and placeholder comments are retained. “Standalone” means
the snippet is a syntactically complete declaration/unit; it does **not** mean
that names such as `Part1` or `Fuel` are defined locally. “Contextual” means the
snippet is a member-level shorthand or otherwise needs an enclosing model
context to parse. “Definitions required” records semantic/name dependencies,
not parser recovery.

## Inventory

### 7.13 Connections, bindings, feature values, and successions

| ID | Clause | Printed page(s) | Parse status | Dependencies | Exact normalized code |
|---|---|---:|---|---|---|
| C01 | Table 11, connection definition | 65 | Standalone | `Part1`, `Part2` must be defined for resolution | `connection def ConnectionDef1 {<br>  end end1 : Part1;<br>  end end2 : Part2;<br>}` |
| C02 | Table 11, connection definition with members | 65 | Standalone | None syntactically; placeholder `/* members */` is intentional | `connection def ConnectionDef1 {<br>  /* members */<br>}` |
| C03 | Table 11, multiplicity connection definition | 65 | Standalone | `Part1`, `Part2` | `connection def ConnectionDef1 {<br>  end [0..1] part end1 : Part1;<br>  end [1..*] part end2 : Part2;<br>}` |
| C04 | Table 11, directed connection definition | 65 | Standalone | `Part1`, `Part2` | `connection def ConnectionDef2 {<br>  end [1..1] part sourceEnd : Part1;<br>  end [1..*] part targetEnd : Part2;<br>}` |
| C05 | Table 11, n-ary connection definition | 66 | Standalone | `Part1`, `Part2`, `Part3` | `connection def ConnectionDef1 {<br>  end [0..1] part end1 : Part1;<br>  end part end2 : Part2;<br>  end part end3 : Part3;<br>}` |
| C06 | Table 11, connection usage with explicit ends | 66 | Standalone | `ConnectionDef1`, `part1`, `part2` | `connection connection1 : ConnectionDef1 {<br>  end end1 ::> part1;<br>  end end2 ::> part2;<br>}` |
| C07 | Table 11, connection usage with members | 66 | Standalone | `ConnectionDef1` | `connection connection1 : ConnectionDef1 {<br>  /* members */<br>}` |
| C08 | Table 11, binary connection shorthand | 66 | Contextual | `ConnectionDef1`, `part1`, `part2`; requires an owning context | `connection connection1 : ConnectionDef1<br>  connect part1 to part2;` |
| C09 | Table 11, directed binary connection shorthand | 66 | Contextual | `ConnectionDef2`, `part1`, `part2`; owning context | `connection connection2 : ConnectionDef2<br>  connect part1 to part2;` |
| C10 | Table 11, n-ary connection shorthand | 66 | Contextual | `ConnectionDef1`, `part1`, `part2`, `part3`; owning context | `connection connection1 : ConnectionDef1<br>  connect (part1, part2, part3);` |
| C11 | Table 11, nested connection | 67 | Standalone | `Part1`-`Part5`, `ConnectionDef1` | `part def Part1 {<br>  part part2 : Part2 {<br>    part part4 : Part4;<br>  }<br>  part part3 : Part3 {<br>    part part5 : Part5;<br>  }<br>  connection connection1 : ConnectionDef1<br>    connect part2.part4 to part3.part5;<br>}` |
| C12 | Table 11, proxy connection | 67 | Standalone | `Part1`-`Part5`, `ConnectionDef1` | `part def Part1 {<br>  part part2 : Part2 {<br>    part part4 : Part4;<br>  }<br>  part part3 : Part3 {<br>    part part5 : Part5;<br>  }<br>  connection connection1 : ConnectionDef1<br>    connect part2.part4 to part3.part5;<br>}` |
| C13 | Table 11, binding connection | 67 | Standalone | `Part1`-`Part4` | `part part1 : Part1 {<br>  part part2 : Part2 {<br>    ref part part4R : Part4;<br>  }<br>  part part3 : Part3 {<br>    part part4 : Part4;<br>  }<br>  bind part2.part4R = part3.part4;<br>}` |
| C14 | Table 11, compact binding connection | 68 | Standalone | `Part1`-`Part4` | `part def Part1 {<br>  part part2:part2 {<br>    ref part part4R:Part4;<br>  }<br>  part part3:part3 {<br>    part part4:Part4;<br>  }<br>  bind part2.part4R = part3.part4;<br>}` |
| C15 | 7.13.2 related-elements example, definition | 68 | Standalone | `Hub`, `Device`, `Real` | `// The related elements of this connection definition<br>// are the part definitions Hub and Device.<br>connection def DeviceConnection {<br>  end part hub : Hub;<br>  end part device : Device;<br><br>  // This is a non-end feature of the connection definition.<br>  attribute bandwidth : Real;<br>}` |
| C16 | 7.13.2 related-elements example, usage | 68 | Contextual | `DeviceConnection`, `mainSwitch`, `sensorFeed`; owning workspace | `// The related elements of this connection usage<br>// are the part usages mainSwitch and sensorFeed.<br>connection connection1 : DeviceConnection {<br>  end part hub ::> mainSwitch[1];<br>  end part device ::> sensorFeed[1];<br>}` |
| C17 | 7.13.2 cross subsetting | 69 | Standalone | `Hub`, `Device`, `Real`; feature-chain names | `part def Hub {<br>  ref part connectedDevices [1..*] ordered : Device;<br>}<br>part def Device {<br>  ref part connectingHub [0..1] : Hub;<br>}<br>connection def DeviceConnection {<br>  end part hub : Hub crosses device.connectingHub;<br>  end part device : Device => hub.connectedDevices;<br>  attribute bandwidth : Real;<br>}` |
| C18 | 7.13.2 owned cross features (continued) | 69-70 | Standalone after continuation | `Hub`, `Device`, `Real`; block closes on page 70 | `connection def HubDeviceConnection {<br>  end connectingHub [0..1] ordered part hub : Hub;<br>  end connectedDevices [1..*] part device : Device;<br>  attribute bandwidth : Real;<br>}` |
| C19 | 7.13.2 owned-cross shorthand | 70 | Standalone | `Hub`, `Device`, `Real` | `connection def HubDeviceConnection {<br>  end [0..1] part hub : Hub;<br>  end [1..*] ordered part device : Device;<br>  attribute bandwidth : Real;<br>}` |
| C20 | 7.13.2 n-ary cross features | 70 | Standalone | `Hub`, `Device`, `Protocol` | `connection def ProtocolDeviceConnection {<br>  end [*] part hub : Hub;<br>  end [*] ordered part device : Device;<br>  end [0..1] item protocol : Protocol;<br>}` |
| C21 | 7.13.2 connection usage cross features | 70 | Standalone | `Axle`, `DeviceConnection`, `networkDevices` | `part def NetworkConfiguration {<br>  part networkHubs[*] : Axle;<br>  part networkDevices[*] : Device;<br>  // Connects each one of the networkHubs to at most four of the networkDevices.<br>  connection networkConnections : DeviceConnection {<br>    end [1] part hub references networkHubs;<br>    end [0..4] part device references networkDevices;<br>  }<br>}` |
| C22 | 7.13.2 connection-list shorthand | 71 | Contextual | `DeviceConnection`, `mainSwitch`, `sensorFeed`; owner required | `connection connection1 : DeviceConnection connect (<br>  [1] hub ::> mainSwitch[1], [1] device ::> sensorFeed<br>);` |
| C23 | 7.13.2 ternary shorthand | 71 | Contextual | `axle`, `wheel1`, `wheel2`; owner required | `// This is a ternary connection.<br>// It is equivalent to "connection connect (axle, wheel1, wheel2);"<br>connect (axle, wheel1, wheel2);` |
| C24 | 7.13.2 binary source-to-target shorthand | 71 | Contextual | `DeviceConnection`, `mainSwitch`, `sensorFeed`; owner required | `connection connection1 : DeviceConnection<br>  connect [1] hub ::> mainSwitch to [1] device ::> sensorFeed;` |
| C25 | 7.13.2 unnamed binary shorthand | 71 | Contextual | `leftWheel`, `leftHalfAxle`; owner required | `connect leftWheel to leftHalfAxle;` |
| C26 | 7.13.2 connection specialization | 71 | Standalone | `MonetaryValue`, `LegalEntity`, `Asset`, library `BinaryConnection` | `// Implicitly specializes Connections::BinaryConnection by default.<br>connection def AssetOwnership {<br>  attribute valuationOnPurchase : MonetaryValue;<br>  end [1..*] item owner : LegalEntity; // Implicitly redefines BinaryConnection::source.<br>  end [*] item ownedAsset : Asset; // Implicitly redefines BinaryConnection::target.<br>}<br>connection def SoleOwnership specializes AssetOwnership {<br>  end [1] item owner; // Implicitly redefines Ownership::owner.<br>  // ownedAsset is inherited.<br>}` |
| C27 | 7.13.2 connection usage redefinitions | 72 | Standalone | `DeviceConnection`, `mainSwitch`, `sensorFeed` | `connection connection1 : DeviceConnection {<br>  end [1] part hub ::> mainSwitch; // Implicitly redefines DeviceConnection::hub.<br>  end [1] part device ::> sensorFeed; // Implicitly redefines DeviceConnection::device.<br>}` |
| C28 | 7.13.3 binding usage | 72 | Standalone | `Fuel`, `Vehicle` owner context | `part def Vehicle {<br>  part fuelTank {<br>    out fuelFlowOut : Fuel;<br>  }<br>  part engine {<br>    in fuelFlowIn : Fuel;<br>  }<br>  binding fuelFlowBinding<br>    bind fuelTank.fuelFlowOut = engine.fuelFlowIn;<br><br>  // The following is equivalent to the above, but<br>  // without the name.<br>  bind fuelTank.fuelFlowOut = engine.fuelFlowIn;<br>}` |
| C29 | 7.13.4 bound/default feature values | 72 | Standalone | `Natural`, `Integer`, `Rational`, `TestRecord`; `sum`/`size` library expressions | `attribute monthsInYear : Natural = 12;<br>item def TestRecord {<br>  attribute scores[1..*] : Integer;<br>  derived attribute averageScore[1] : Rational = sum(scores)/size(scores);<br>  attribute cutoff : Integer default = 0.75 * averageScore;<br>}` |
| C30 | 7.13.4 fixed initial value | 73 | Standalone | `Natural`; occurrence owner semantics | `part def Counter {<br>  attribute count[1] : Natural := 0;<br>}` |
| C31 | 7.13.4 default feature values | 73 | Standalone | `Real`, `Engine`, `standardEngine` | `part def Vehicle {<br>  attribute mass : Real default 1500.0;<br>  feature engine[1] : Engine default := standardEngine;<br>}` |
| C32 | 7.13.4 inherited default value | 73 | Standalone | `TestRecord`, `Rational`, `averageScore` | `item def TestWithCutoff :> TestRecord {<br>  attribute cutoff : Rational default = 0.75 * averageScore;<br>}` |
| C33 | 7.13.5 named successions | 73 | Standalone | `Focus`, `Shoot`; occurrence usages | `part def Camera {<br>  action focus[*] : Focus;<br>  action shoot[*] : Shoot;<br>  // Each focus may be preceded by a previous focus.<br>  succession multiFocusing<br>    first [0..1] focus then [0..1] focus;<br>  // Each shoot must follow a focus.<br>  first [1] focus then [0..1] shoot;<br>  // The Camera can be focused after shooting.<br>  first [0..1] shoot then focus;<br>}` |
| C34 | 7.13.5 lexical succession shorthand | 73-74 | Standalone after continuation | `Flight` occurrence definition; first two lines continue on page 74 | `occurrence def Flight {<br>  timeslice preflight[1];<br>  then timeslice inflight[1];<br>  then timeslice postflight[1];<br>}` |
| C35 | 7.13.5 expanded succession equivalent | 74 | Standalone | `Flight` occurrence definition | `// The above is equivalent to the following.<br>occurrence def Flight {<br>  timeslice preflight[1];<br>  first preflight then inflight;<br>  timeslice inflight[1];<br>  first inflight then postflight;<br>  timeslice postflight[1];<br>}` |

### 7.14 Interfaces

| ID | Clause | Printed page(s) | Parse status | Dependencies | Exact normalized code |
|---|---|---:|---|---|---|
| C36 | Table 12, interface definition | 75 | Standalone | `Port1`, `Port2` | `interface def InterfaceDef1 {<br>  end port1:Port1;<br>  end port2:Port2;<br>}` |
| C37 | Table 12, interface definition with members | 75 | Standalone | None syntactically; placeholder retained | `interface def InterfaceDef1 {<br>  /* members */<br>}` |
| C38 | Table 12, interface usage with ends | 75 | Standalone | `InterfaceDef1`, `pa`, `pb` | `interface interface1 : InterfaceDef1 {<br>  end port1 :> pa;<br>  end port2 :> pb;<br>}` |
| C39 | Table 12, interface usage with members | 75 | Standalone | `InterfaceDef1` | `interface interface1 : InterfaceDef1 {<br>  /* members */<br>}` |
| C40 | Table 12, interfaces compartment | 75 | Contextual | `InterfaceDef1`, `InterfaceDef2`; enclosing compartment | `{<br>  interface interface1 : InterfaceDef1 [1..*];<br>  interface interface2 : InterfaceDef2;<br>  /* ... */<br>}` |
| C41 | Table 12, interface usage between parts | 75 | Standalone | `Part1`, `Part2`, `P4`, `P2`, `InterfaceDef1` | `part part1:Part1 {<br>  port p4:P4;<br>}<br>part part2:Part2 {<br>  port p2:P2;<br>}<br>interface interface1 : InterfaceDef1<br>  connect part1.p4 to part2.p2;` |
| C42 | Table 12, interface as node | 76 | Standalone | `P1`-`P3`, `Pa`, `Part1`, `Part2`, `InterfaceDef2` | `port def Pa {<br>  port p1 : P1;<br>  port p2 : P2;<br>  port p3 : P3;<br>}<br>part def Part1 {<br>  port pa : Pa;<br>}<br>part def Part2 {<br>  port pb : ~Pa;<br>}<br>interface def InterfaceDef2 {<br>  end :>> source : Pa;<br>  end :>> target : ~Pa;<br>}<br>part part0 {<br>  part part1 : Part1;<br>  part part2 : Part2;<br><br>  interface interface2 : InterfaceDef2<br>    connect source ::> part1.pa to target ::> part2.pb {<br>      interface source.p1 to target.p1;<br>      interface source.p2 to target.p2;<br>      interface source.p3 to target.p3;<br>    }<br>}` |
| C43 | Table 12, interface as node with flow | 77 | Standalone | `P1`, `P2`, `Item1`, `Item2`, `Part1`, `Part2`, `Interface2` | `port def Pa {<br>  out item i1Out : Item1;<br>  in item i2In : Item2;<br>}<br>interface def Interface2 {<br>  end supplierP : Pa;<br>  end consumerP : ~Pa;<br>  flow supplierP.i1Out to consumerP.i1Out;<br>  flow consumerP.i2In to supplierP.i2In;<br>}<br>part part0 {<br>  part part1 : Part1 {<br>    port pa : Pa;<br>  }<br>  part part2 : Part2 {<br>    port pb : ~Pa;<br>  }<br>  interface if2 : Interface2 connect part1.pa to part2.pb;<br>}` |
| C44 | 7.14.2 interface shorthand | 77 | Contextual | `Fuel`, `FuelingPort`, `FuelingInterface`, `fuelTank`, `engine` | `port def FuelingPort {<br>  out fuel : Fuel;<br>}<br>interface def FuelingInterface {<br>  end fuelOutPort : FuelingPort;<br>  end fuelInPort : ~FuelingPort;<br>}<br>interface fuelLine : FuelingInterface<br>  connect fuelTank.fuelingPort to engine.fuelingPort;<br>// The following is equivalent to the above, except<br>// for not using a specialized interface definition.<br>interface fuelTank.fuelingPort to engine.fuelingPort;` |
| C45 | 7.14.2 automatic interface targeting | 78 | Standalone | `Request`, `Response`, `clientPort`, `serverPort` | `part def DistributedSystem {<br>  item def Request;<br>  item def Response;<br>  part client {<br>    port clientPort;<br>    action clientBehavior {<br>      send new Request() via clientPort;<br>      then accept Response via clientPort;<br>    }<br>  }<br><br>  part server {<br>    port serverPort;<br>    action serverBehavior {<br>      accept Request via serverPort;<br>      then send new Response() via serverPort;<br>    }<br>  }<br><br>  // Transfers from the clientPort automatically target the serverPort<br>  // and vice versa.<br>  interface client.clientPort to server.serverPort;<br>}` |

### 7.15 Allocations

| ID | Clause | Printed page(s) | Parse status | Dependencies | Exact normalized code |
|---|---|---:|---|---|---|
| C46 | Table 13, allocation definition | 79 | Standalone | None | `allocation def AllocationDef1;` |
| C47 | Table 13, allocation definition with members | 79 | Standalone | None syntactically; placeholder retained | `allocation def AllocationDef1 {<br>  /* members */<br>}` |
| C48 | Table 13, allocation usage | 79 | Contextual | `AllocationDef1`; owning context | `allocation allocation1 : AllocationDef1;` |
| C49 | Table 13, allocation usage with members | 79 | Contextual | `AllocationDef1`; owning context | `allocation allocation1 : AllocationDef1 {<br>  /* members */<br>}` |
| C50 | Table 13, allocated compartment | 79 | Contextual | `part1`, `part2`, `part3`; owning part context | `part part3 {<br>  allocate part1 to part3;<br>  allocate part3 to part2;<br>}` |
| C51 | Table 13, allocation | 79 | Contextual | `Part1`, `Part2`; owning context | `part part1 : Part1;<br>part part2 : Part2;<br>allocate part1 to part2;` |
| C52 | Table 13, allocation with sub-allocation | 79 | Contextual | `Part1`, `Part2`, `action1`, `action2`; owning context | `part part1 : Part1 {<br>  perform action1;<br>}<br>part part2 : Part2 {<br>  perform action2;<br>}<br>allocate part1 to part2 {<br>  allocate part1.action1 to part2.action2;<br>}` |
| C53 | 7.15.2 allocation definition and usage | 80 | Standalone | `LogicalComponent`, `PhysicalAssembly`, `LogicalSystem`, `PhysicalDevice`, `LogicalToPhysicalAllocation` | `part def LogicalSystem {<br>  part component : LogicalComponent;<br>}<br>part def PhysicalDevice {<br>  part assembly : PhysicalAssembly;<br>}<br>allocation def LogicalToPhysicalAllocation {<br>  end part logical : LogicalSystem;<br>  end part physical : PhysicalDevice;<br><br>  // This is a nested sub-allocation.<br>  allocate logical.component to physical.assembly;<br>}<br>part system : LogicalSystem;<br>part device : PhysicalDevice;<br>allocation systemToDevice : LogicalToPhysicalAllocation<br>  allocate logical ::> system to physical ::> device;` |

### 7.16 Flows and messages

| ID | Clause | Printed page(s) | Parse status | Dependencies | Exact normalized code |
|---|---|---:|---|---|---|
| C54 | Table 14, flow | 81 | Standalone | `Action1`, `Action2`, `Item1` | `action action1:Action1 {<br>  out item1:Item1;<br>}<br>action action2:Action2 {<br>  in item1:Item1;<br>}<br>flow action1.item1 to action2.item1;` |
| C55 | Table 14, flow as node | 82 | Standalone | `Item1`, `Action1`, `Action2`, `FlowConnection`; nested item names | `item def Item1 {<br>  item subItem1;<br>  item subItem2;<br>  item subItem3;<br>}<br>action action1 : Action1 {<br>  out item1 : Item1;<br>}<br>action action2 : Action2 {<br>  in item2 : Item1;<br>}<br>flow flow1_2 from action1.item1 to action2.item2 {<br>  flow source.item1.subItem1 to target.item2.subItem1;<br>  flow source.item1.subItem2 to target.item2.subItem2;<br>  flow source.item1.subItem3 to target.item2.subItem3;<br>}` |
| C56 | Table 14, flows compartment | 82 | Contextual | `ItemDef`, `part1`, `part2`, `action1`, `action2`; enclosing context | `{<br>  flow flow1 of ItemDef from part1.port1 to part2.port2;<br>  flow flow2 from action1.output to action2.input;<br>  flow action1.output to action2.input;<br>  succession flow action1.output to action2.input;<br>  message msg from part1 to part2;<br>}` |
| C57 | Table 14, message in interconnection view | 82 | Standalone | `Part1`, `Part2`, `Item1`, `ev1`, `ev2` | `part part1 : Part1 {<br>  event occurrence ev1;<br>}<br>part part2 : Part2 {<br>  event occurrence ev2;<br>}<br>message of item1 : Item1 from part1.ev1 to part2.ev2;` |
| C58 | Table 14, message in sequence view | 83 | Standalone | `Part1`, `Part2`, `ev1`, `ev2` | `occurrence {<br>  part part1 : Part1 {<br>    event occurrence ev1;<br>  }<br>  part part2 : Part2 {<br>    event occurrence ev2;<br>  }<br>  message msg1 from part1.ev1 to part2.ev2;<br>}` |
| C59 | 7.16.2 flow definition | 83 | Standalone | `Fuel`, `FuelTank`, `Engine`; `payload` feature | `flow def FuelFlow {<br>  ref item :>> payload : Fuel;<br>  end tank : FuelTank;<br>  end eng : Engine;<br>}` |
| C60 | 7.16.2 message usage (continued) | 83-84 | Standalone after continuation | `ControlSignal`, `controller.sendControl`, `engine.receiveControl`; `Vehicle` context | `part def Vehicle {<br>  attribute def ControlSignal;<br>  part controller {<br>    event occurrence sendControl;<br>  }<br>  part engine {<br>    event occurrence receiveControl;<br>  }<br>  message of ControlSignal from controller.sendControl to engine.receiveControl;<br>}` |
| C61 | 7.16.2 streaming flow usage | 84 | Standalone | `FuelTank`, `Engine`, `Fuel`, `FuelFlow`; `Vehicle` context | `part def Vehicle {<br>  part fuelTank : FuelTank {<br>    out fuelOut : Fuel;<br>  }<br>  part engine : Engine {<br>    in fuelIn : Fuel;<br>  }<br>  // This flow usage actually connects the fuelTank to the<br>  // engine. The transfer moves Fuel from fuelOut to fuelIn.<br>  flow fuelFlow : FuelFlow of flowingFuel : Fuel<br>    from fuelTank.fuelOut to engine.fuelIn;<br>  // The following is equivalent to the above,<br>  // and leaving the flow definition and payload implicit.<br>  flow fuelTank.fuelOut to engine.fuelIn;<br>}` |
| C62 | 7.16.2 succession flow usage | 84 | Standalone | `Focus`, `Shoot`, `Image` | `action def TakePicture {<br>  action focus : Focus {<br>    out image : Image;<br>  }<br>  action shoot : Shoot {<br>    in image : Image;<br>  }<br>  // The use of a succession flow usage means that focus must<br>  // complete before the image is transferred, after which shoot can begin.<br>  succession flow focus.image to shoot.image;<br>}` |

### 7.17 Actions

| ID | Clause | Printed page(s) | Parse status | Dependencies | Exact normalized code |
|---|---|---:|---|---|---|
| C63 | Table 15, action definition | 87 | Standalone | None | `action def ActionDef1;` |
| C64 | Table 15, action definition with members | 87 | Standalone | None syntactically; placeholder retained | `action def ActionDef1 {<br>  /* members */<br>}` |
| C65 | Table 15, action usage | 88 | Contextual | `ActionDef1`; owning context | `action action1 : ActionDef1;` |
| C66 | Table 15, action usage with members | 88 | Contextual | `ActionDef1`; owning context | `action action1 : ActionDef1 {<br>  /* members */<br>}` |
| C67 | Table 15, action with parameters | 88 | Standalone | `ItemDef1`, `ItemDef2`; parameter names are local | `item def ItemDef1 {<br>  in item 'item1.1';<br>  out item 'item1.2';<br>  in item 'item1.3';<br>}<br>action action1 {<br>  inout param1 :ItemDef1;<br>  out param2 : ItemDef2;<br>}` |
| C68 | Table 15, action graphical-compartment flow | 88 | Standalone | `Action1`, `Action2`, `Action3`; `input1`/`output1` local | `action action1 : Action1 {<br>  in input1;<br>  bind input1 = action2.input2;<br>  action action2 : Action2 {<br>    in input2;<br>    out output2;<br>  }<br>  flow action2.output2 to action3.input3;<br>  action action3 : Action3 {<br>    in input3;<br>    out output3;<br>  }<br>  bind action3.output3 = output1;<br>  out output1;<br>}` |
| C69 | Table 15, actions compartment | 89 | Contextual | `ActionDef1`, `ActionDef2`, `ActionDef3R`, etc.; owner required | `{<br>  action action1 : ActionDef1 [1..*] ordered nonunique;<br>  /* ... */<br>  perform action action10;<br>  action action11 {<br>    action 'action11.1';<br>    action 'action11.2';<br>  }<br>}` |
| C70 | Table 15, perform-actions compartment | 89 | Contextual | `ActionDef1`; owner required | `{<br>  perform action action1 : ActionDef1 [1..*] ordered nonunique;<br>  /* ... */<br>}` |
| C71 | Table 15, perform-actions swimlanes | 90 | Standalone | `PartDef0`, `PartDef1`, `PartDef2`, `ActionDef1`-`ActionDef4` | `package SwimLanes {<br>  part def Part0;<br>  part def Part1;<br>  part def Part2;<br>  part part0 : PartDef0 {<br>    perform action0;<br>    part part1 : PartDef1 {<br>      perform action0.action1;<br>      perform action0.action4;<br>    }<br>    part part2 : PartDef2 {<br>      perform action0.action2;<br>      perform action0.action3;<br>    }<br>  }<br>  action action0 {<br>    action action1;<br>    action action2;<br>    action action3;<br>    action action4;<br>    first start then action1;<br>    first action1 then action2;<br>    first action2 then action3;<br>    first action3 then action4;<br>    first action4 then done;<br>  }<br>}` |
| C72 | Table 15, parameters compartment | 91 | Contextual | `ParamDef` names and `expression1`; owner required | `{<br>  in param1 : ParamDef [1..*] ordered nonunique;<br>  /* ... */<br>}` |
| C73 | Table 15, conditional succession alternatives | 91 | Contextual | `Action1`, `Action2`, `guard1`; owner required | `action action1 : Action1;<br>action action2 : Action2;<br>succession action1<br>  if guard1 then action2;<br><br>or<br><br>action action1 : Action1;<br>if guard1 then action2;<br>action action2 : Action2;` |
| C74 | Table 15, actions with control nodes | 92 | Contextual | `action1`-`action4`, `guard1`, `guard2`; owner required | `first start;<br>then fork fork1;<br>  then action1;<br>  then action2;<br>action action1;<br>  then join1;<br>action action2;<br>  then join1;<br>join join1;<br>then decide decision1;<br>  if guard2 then action3;<br>  if guard1 then action4;<br>action action3;<br>  then merge1;<br>action action4;<br>  then merge1;<br>merge merge1;<br>then terminate;` |
| C75 | Table 15, until loop (textual body) | 93 | Standalone | `Integer`; action-control library semantics | `action actionWithLoop1 {<br>  attribute x:Integer;<br>  attribute increment:Integer = 1;<br>  attribute y:Integer;<br>  first start;<br>  then assign x := 1;<br>  then action loop1<br>  loop {<br>    assign y := 2*x;<br>    then assign x := x + increment;<br>  } until x >= 10;<br>  then done;<br>}` |
| C76 | Table 15, until loop (graphical-body cell) | 94 | Standalone | `Integer`; duplicate textual cell intentionally retained | `action actionWithLoop1 {<br>  attribute x:Integer;<br>  attribute increment:Integer = 1;<br>  attribute y:Integer;<br>  first start;<br>  then assign x := 1;<br>  then action loop1<br>  loop {<br>    assign y := 2*x;<br>    then assign x := x + increment;<br>  } until x >= 10;<br>  then done;<br>}` |
| C77 | Table 15, while loop | 95 | Standalone | `Integer`; action-control library semantics | `action actionWithLoop2 {<br>  in attribute x:Integer;<br>  out attribute y:Integer;<br>  attribute increment:Integer = 1;<br>  first start;<br>  then assign y := 0;<br>  then action loop2<br>  while x < 10 {<br>    assign y := 2*x;<br>    then assign x := x + increment;<br>  }<br>  then done;<br>}` |
| C78 | Table 15, for loop | 96 | Standalone | `Integer`; `n` input and loop variable local | `action actionWithLoop3 {<br>  in attribute n:Integer;<br>  out attribute y:Integer;<br>  first start;<br>  then assign y := 0;<br>  then action forLoop1<br>  for i : Integer in 1..n {<br>    assign y := y + i;<br>  }<br>  then done;<br>}` |
| C79 | Table 15, if-then structured action | 96 | Standalone | `Integer`; `a` input/output local | `action {<br>  inout attribute a : Integer;<br>  action ifThenAction if a < 0 {<br>    assign a := -a;<br>  }<br>}` |
| C80 | Table 15, if-then-else structured action | 97 | Standalone | `Integer`; `a`, `b` local | `action {<br>  in attribute a : Integer;<br>  out attribute b : Integer;<br>  action ifThenElseAction if a >= 20 {<br>    assign b := 100;<br>  } else {<br>    assign b := 0;<br>  }<br>}` |
| C81 | Table 15, accept action | 97 | Contextual | `Scene`, `viewPort`; owner/port context | `port viewPort;<br>item def Scene;<br>action trigger1 accept<br>  scene : Scene via viewPort;` |
| C82 | Table 15, accept action with succession | 97 | Contextual | `Scene`, `viewPort`, `action2`; owner context | `port viewPort;<br>item def Scene;<br>action trigger1 accept<br>  scene : Scene via viewPort;<br>succession flow from<br>  trigger1.scene to action2.scene;<br>action action2 {<br>  in item scene : Scene;<br>}` |
| C83 | Table 15, send action | 97 | Contextual | `Picture`, `displayPort`; owner/port context | `item def Picture;<br>port displayPort;<br>action send1 send new Picture() via displayPort;` |
| C84 | Table 15, send action with succession flow | 98 | Contextual | `Picture`, `displayPort`, `shoot`; owner context | `item def Picture;<br>port displayPort;<br>action shoot {<br>  out item picture : Picture;<br>}<br>action send1 send via displayPort;<br>succession flow from shoot.picture to send1.payload;` |
| C85 | Table 15, accept/send action flow | 99 | Standalone | `Scene`, `camera`, `screen`, `Focus`, `Shoot`, `Picture`; external port/item types | `item def Scene;<br>part camera {<br>  port viewPort;<br>  port displayPort;<br>  perform action takePicture {<br>    action trigger accept scene : Scene {<br>      in :>> receiver = viewPort;<br>    }<br>    then action focus {<br>      in item scene = trigger.scene;<br>      out item image;<br>    }<br>    succession flow from focus.image to shoot.image;<br>    action shoot {<br>      in item image;<br>      out item picture;<br>    }<br>    then action sendPicture send {<br>      in picture :>> payload = shoot.picture;<br>      in :>> sender = camera.displayPort;<br>    }<br>  }<br>}<br>part screen {<br>  port displayPort;<br>}` |
| C86 | 7.17.2 action definition and usage | 100 | Standalone | `Scene`, `Picture`, `Focus`, `Shoot`, `Image`; action definitions/types | `action def TakePicture {<br>  // The following two features are considered parameters.<br>  in scene : Scene;<br>  out picture : Picture;<br><br>  bind focus.scene = scene;<br>  action focus : Focus { in scene; out image; }<br>  first focus then shoot;<br>  flow focus.image to shoot.image;<br>  action shoot : Shoot { in image; out picture; }<br>  bind picture = focus.picture;<br>}` |
| C87 | 7.17.2 multiple-superclassification parameters | 100 | Standalone | None beyond action language | `action def A { in a1; out a2; }<br>action def B { in b1; out b2; }<br>action def C specializes A, B {<br>  in c1 redefines a1 redefines b1;<br>  out c2 redefines a2 redefines b2;<br>}` |
| C88 | 7.17.2 implicit parameter redefinitions | 100 | Standalone | `A`, `B` action definitions | `action def A1 :> A { in aa; } // aa redefines A::a1, A::a2 is inherited.<br>action def B1 :> B { in b1; out b2; inout b3; } // Redefinitions are implicit.<br>action def C1 :> A1, B1 { in c1; out c2; inout c3; }` |
| C89 | 7.17.2 specialized action usage | 100 | Contextual | `Focus`; containing action context | `action focus : Focus {<br>  // Parameters redefine parameters of Focus.<br>  in scene;<br>  out image;<br>}<br><br>action refocus subsets focus; // Parameters are inherited.` |
| C90 | 7.17.2 nested action binding/flow (continued) | 100-101 | Standalone after continuation | `ProvidePower`, `GeneratePower`, `TransmitPower`, `FuelCmd`, `Torque`; block closes on page 101 | `action providePower : ProvidePower {<br>  in fuelCmd : FuelCmd;<br>  action generatePower : GeneratePower {<br>    in fuelCmd : FuelCmd = providePower::fuelCmd;<br>    out generatedTorque : Torque;<br>  }<br>  flow generatePower.generatedTorque<br>    to transmitPower.generatedTorque;<br>  action transmitPower : TransmitPower {<br>    in generatedTorque : Torque;<br>    out transmittedTorque;<br>    // ...<br>  }<br>}` |

## Counts and page coverage

The row count is by example/cell, not by physical occurrence of a continued
row. Of the 90 rows, 57 are examples taken from table textual-notation cells
and 33 are prose examples/declarations. Twelve table examples retain a
placeholder such as `/* members */` or `/* ... */`. Four rows cross a page
boundary (C18, C34, C60, C90). C75/C76 are deliberately retained as two rows
because they are two distinct table cells with identical textual code.

| Printed page | New rows starting on page | Rows continuing in/out | IDs starting on page |
|---:|---:|---:|---|
| 65 | 4 | 0 | C01-C04 |
| 66 | 6 | 0 | C05-C10 |
| 67 | 3 | 0 | C11-C13 |
| 68 | 3 | 0 | C14-C16 |
| 69 | 2 | C18 starts | C17-C18 |
| 70 | 3 | C18 continues | C19-C21 |
| 71 | 5 | 0 | C22-C26 |
| 72 | 3 | 0 | C27-C29 |
| 73 | 5 | C34 starts | C30-C34 |
| 74 | 1 | C34 continues | C35 |
| 75 | 6 | 0 | C36-C41 |
| 76 | 1 | 0 | C42 |
| 77 | 2 | 0 | C43-C44 |
| 78 | 1 | 0 | C45 |
| 79 | 7 | 0 | C46-C52 |
| 80 | 1 | 0 | C53 |
| 81 | 1 | 0 | C54 |
| 82 | 3 | 0 | C55-C57 |
| 83 | 3 | C60 starts | C58-C60 |
| 84 | 2 | C60 continues | C61-C62 |
| 85 | 0 | 0 | — |
| 86 | 0 | 0 | — |
| 87 | 2 | 0 | C63-C64 |
| 88 | 4 | 0 | C65-C68 |
| 89 | 2 | 0 | C69-C70 |
| 90 | 1 | 0 | C71 |
| 91 | 2 | 0 | C72-C73 |
| 92 | 1 | 0 | C74 |
| 93 | 1 | 0 | C75 |
| 94 | 1 | 0 | C76 |
| 95 | 1 | 0 | C77 |
| 96 | 2 | 0 | C78-C79 |
| 97 | 4 | 0 | C80-C83 |
| 98 | 1 | 0 | C84 |
| 99 | 1 | 0 | C85 |
| 100 | 5 | C90 continues to 101 | C86-C90 |

The “new rows” column sums to 90. Pages 65-100 were all inspected; pages 85
and 86 contain prose only in the relevant area, so their zero counts are
intentional. The only in-scope example whose closing lines lie outside the
requested interval is C90, completed on printed page 101. The page-101
`fork fork1` example was inspected but is excluded because it begins after the
in-scope C90 continuation and is outside the requested page range.

## Exclusion ledger

* **Graphical-notation labels:** Every code-like label inside the “Graphical
  Notation” column or a diagram was excluded, including names such as
  `part1 : Part1`, `end1 : Part1`, `x := 1`, `a < 0`, and the labels in the
  swimlane/control-node diagrams. They are diagram labels, not textual-
  notation cells. This applies throughout pages 65-67, 75-77, 79, 81-83,
  87-99.
* **Empty graphical compartments:** The “Connections Compartment” row on
  page 67 and the “Performed By Compartment” row on page 92 have no textual
  notation. They contribute no example row.
* **Inline prose quotations and equivalence mentions:** Quoted strings such as
  the prose mention of `connection connect (axle, wheel1, wheel2);` are not
  counted separately when the actual code block is present (C23). Likewise,
  prose keywords (`crossing`, `references`, `happensBeforeLinks`, etc.) are
  explanatory text, not examples.
* **Metamodel/reference tables and links:** Clause references, library names,
  grammar/abstract-syntax links, and the page-101 Table 16 mapping of control
  keywords to library definitions are not SysML textual examples. Table 16 is
  outside the requested range except for the inspected continuation page.
* **Page-101 control-node example:** The complete `fork fork1` block on page
  101 was not counted because it starts after C90 and is outside pages 65-100;
  it is not needed to close any in-scope example.
* **OCR/layout artifacts:** PDF extraction sometimes split tokens (for
  example, `sourceEnd`, `targetEnd`, and `1..*`) across lines. The report uses
  the visually confirmed token sequence. No inferred examples were added from
  extraction artifacts.

## Audit conclusion

The requested interval contains textual examples across clauses 7.13 through
7.17, with no missing page in the visual pass. The complete inventory is
C01-C90 above. For parser-fixture use, prefer rows marked Standalone, while
rows marked Contextual should be embedded in an appropriate package/part/action
owner and supplied with the named definitions listed in Dependencies.
