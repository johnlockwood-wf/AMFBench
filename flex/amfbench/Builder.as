package amfbench
{
    public class Builder
    {
        public static function simple(num:int):Array
        {
            var ret:Array = [];
    
            for (var i:int=0; i < num; i++)
            {
                var obj:Object = new Object();
    
                obj.number = 10;
                obj.float = 3.24;
                obj.string = 'foo number ' + i;
    
                ret.push(obj);
            }
    
            return ret;
        }
    
        public static function complex(num:int):Array
        {
            var ret:Array = [];
    
            for (var i:int=0; i < num; i++)
            {
                var obj:SomeClass = new SomeClass();
    
                obj._null = null;
                obj.list = ['test', 'tester'];
                obj.dict = new Object();
                obj.dict.test = 'ignore';
                obj.string_ref = 'string_ref';
    
                obj.number = i;
                obj.float = 3.14;
                obj.unicode = 'ƒøø'                    
    
                obj.sub_obj = new SomeClass();
                obj.sub_obj.number = i;
                obj.ref = obj.sub_obj;
    
                ret.push(obj);
            }
    
            return ret;
        }
    
        public static function _static(num:int):Array
        {
            var ret:Array = [];
    
            for (var i:int=0; i < num; i++)
            {
                var obj:SomeStaticClass = new SomeStaticClass();

                obj.name = 'name ' + i;
                obj.score = 5.5555555;
                obj.rank = i;

                ret.push(obj);
            }
    
            return ret;
        }
    
        public static function reference(num:int):Array
        {
            var ret:Array = [];
            var obj:Object = new Object();
    
            obj.foo = 'bar'
    
            for (var i:int = 0; i < num; i++)
            {
                ret.push(obj);
            }

            return ret;
        }

        public static function build(name:String, num:int):Array
        {
            var f:Function;

            if (name == 'simple')
                return simple(num);
            if (name == 'complex')
                return complex(num);
            if (name == 'static')
                return _static(num);
            if (name == 'reference')
                return reference(num);

            throw new Error('Unknown build name');
        }
    }
}
