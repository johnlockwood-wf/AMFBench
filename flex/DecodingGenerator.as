package {
  import flash.display.Sprite;
  import flash.net.NetConnection;
  import flash.net.Responder;
  import flash.net.ObjectEncoding;
  import flash.text.TextField;

  import amfbench.Builder;

  public class DecodingGenerator extends Sprite {

    // Gateway connection object
    public var gateway:NetConnection;

    public var gw_url:String = "http://localhost:8080/gw";

    // state vars for building
    public var op:int = 0;
    public var num:int = 0;
    public var encoding:int = 0;

    public var encodings:Array = [ObjectEncoding.AMF0, ObjectEncoding.AMF3];
    public var operations:Array = ['simple', 'complex', 'static', 'reference'];
    public var numbers:Array = [1000, 2000, 5000, 10000, 20000, 50000];

    public function DecodingGenerator():void
    {
        gateway = new NetConnection();

        gateway.connect(gw_url);

        build();
    }

    public function build():void
    {
        var param:Array = Builder.build(operations[op], numbers[num]);
        var responder:Responder = new Responder(onResult, onFault);

        gateway.objectEncoding = encodings[encoding];

        gateway.call(operations[op] + '-' + numbers[num], responder, param);
    }

    // Result handler method
    public function onResult(result:*):void
    {
        num += 1;

        if (num >= numbers.length)
        {
            op += 1;
            num = 0;
        }

        if (op >= operations.length)
        {
            op = 0;
            encoding += 1;
        }

        if (encoding >= encodings.length)
        {
          var display_txt:TextField = new TextField();
          display_txt.text = "All done!";

          addChild(display_txt);

          return; // we're done
        }

        build();
    }

    public function onFault(error:*): void
    {
        // diaf
        onResult(null);
    }
  }
}