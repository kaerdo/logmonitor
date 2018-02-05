# logmonitor

批量日志监控报警，适用于集中式日志分析场景

1. zookeeper分发配置到各台机器agent    
2. 使用watchdog监控文件,动态操作文件  
3. 动态调整报警阀值和报警方式，可自定义日志解析式
4. 每个日志文件支持多个rule



配置信息:  
```
{
  "name": xxxx,
  "expression": "xxx",
  "interval": 1,
  "threshold" : {"min": 0, "max": 0},
  "contacts": {"mail": "xxxx", "mobile": "xxxxx"}
}
```

RESTful API:  
```
{
	"filename":"/test/abc",
	"rule":{
		"name":"rule_test1",
		"expression":".*",
		"interval":1,
		"threshold":{
			"min": 5, 
			"max": 10
		},
			"contacts": {
				"mail": "mail_test", 
				"mobile": 123123123
			}
	}
}

```

启动参数  
```
python app.py --help

  --bind                           Host or bind_IP (default 0.0.0.0)
  --port                           Port (default 8005)
  --zkconnect                      zookeeper connect info (default
                                   127.0.0.1:2181)
  --zkroot                         zk root directory (default /logmonitor)
```
