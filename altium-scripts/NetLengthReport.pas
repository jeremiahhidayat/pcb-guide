{ NetLengthReport.pas - Altium DelphiScript
  Sums routed track + arc length per net and writes <board>_netlengths.csv.
  A quick, scriptable cross-check of the PCB panel's routed lengths - useful in design reviews
  and for exporting lengths into a timing budget spreadsheet (Chapter 17).

  Note: pad-to-pad xSignal lengths, via barrel lengths and pin-package lengths are NOT included.
  Use Altium's xSignals for timing-critical matching; use this for reporting.

  Run: File > Run Script... > NetLengthReport.pas > RunNetLengthReport }

Procedure RunNetLengthReport;
Var
    Board    : IPCB_Board;
    Iterator : IPCB_BoardIterator;
    Prim     : IPCB_Primitive;
    Lengths  : TStringList;
    Csv      : TStringList;
    NetName  : String;
    Len      : Double;
    Sweep    : Double;
    I        : Integer;
    OutPath  : String;
Begin
    Board := PCBServer.GetCurrentPCBBoard;
    If Board = Nil Then
    Begin
        ShowMessage('Open a PCB document first.');
        Exit;
    End;

    Lengths := TStringList.Create;   { Name=Value pairs: net=length_mm }

    Iterator := Board.BoardIterator_Create;
    Iterator.AddFilter_ObjectSet(MkSet(eTrackObject, eArcObject));
    Iterator.AddFilter_LayerSet(SignalLayers);
    Iterator.AddFilter_Method(eProcessAll);

    Prim := Iterator.FirstPCBObject;
    While Prim <> Nil Do
    Begin
        If Prim.Net <> Nil Then
        Begin
            NetName := Prim.Net.Name;
            If Prim.ObjectId = eTrackObject Then
                Len := Sqrt(Sqr(CoordToMMs(Prim.x2) - CoordToMMs(Prim.x1)) +
                            Sqr(CoordToMMs(Prim.y2) - CoordToMMs(Prim.y1)))
            Else
            Begin
                { arc length = r * theta (radians); handle wrap-around }
                Sweep := Prim.EndAngle - Prim.StartAngle;
                If Sweep < 0 Then Sweep := Sweep + 360;
                Len := CoordToMMs(Prim.Radius) * Sweep * Pi / 180;
            End;

            I := Lengths.IndexOfName(NetName);
            If I < 0 Then
                Lengths.Add(NetName + '=' + FloatToStr(Len))
            Else
                Lengths.Values[NetName] := FloatToStr(StrToFloat(Lengths.Values[NetName]) + Len);
        End;
        Prim := Iterator.NextPCBObject;
    End;
    Board.BoardIterator_Destroy(Iterator);

    Lengths.Sort;
    Csv := TStringList.Create;
    Csv.Add('Net,RoutedLength_mm');
    For I := 0 To Lengths.Count - 1 Do
        Csv.Add(Lengths.Names[I] + ',' + FormatFloat('0.000', StrToFloat(Lengths.ValueFromIndex[I])));

    OutPath := ChangeFileExt(Board.FileName, '') + '_netlengths.csv';
    Csv.SaveToFile(OutPath);
    ShowMessage(IntToStr(Lengths.Count) + ' nets written to ' + OutPath);
    Lengths.Free;
    Csv.Free;
End;
