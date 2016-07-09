PPS -- Python PS
================

Linux `ps -aux` command wrapper by python, 用 Python 对命令 `ps -aux` 进行简单的封装。

## 接口说明

#### class UnfoundException()

异常类，当文件、进程等找不到时会抛出该异常


#### class CMDOutException()

异常类，当电泳 Shell 命令出错，或者输出结果不符合预期时会抛出该异常


#### class Process(pid)

进程类，将 `ps -aux` 输出的每一列作为进程对象的属性。进程对象的方法如下：

- Process.update()

更新进程信息。该方法会在初始化对象时默认被调用一次。由于进程的运行信息是动态变化用，可以用该方法实时更新进程的信息。

- Process.kill()

杀死进程。该方法持续向进程发送 SIGTERM 信号，直到进程被关闭。

- Process.to_dict()

将进程信息转化为 dict。该方法仅仅为了某些场合的方便，一般情况不建议调用，因为 Python 的字典是弱引用，大量的调用该方法可能会出现内存泄露。

#### processes()

获取所有进程信息，返回一个迭代器。该方法在调用时先捕获该时刻 `ps -aux` 列出的所有进程的 pid，然后再迭代这些进程的信息。

**调用该函数时需要注意:**

由于调用 processes() 与通过迭代器迭代到一个进程的信息之间存在一定的时间间隔，所以你获得的信息是迭代时的实时信息，而不是调用 processes() 时的信息。因此，该方法存在这样的一些缺陷：在调用 processes() 时捕获到的进程，在迭代时获取不到该进程的信息，因为该进程可能已经退出；无法捕获到迭代过程中新产生的进程。

实际上我认为该方法的应用场景不多，也不建议使用该方法。我们大多数情况下只需要获取某一个进程的信息。

#### mem_percent()

返回系统总的内存占用百分比。通过读取 `/proc/meminfo` 文件获取，计算公式为：

```
(MemTotal - MemFree - Buffers - Cached)/MemTotal * 100
```

#### cpu_percent()

返回 CPU 总的使用率百分比。通过读取 `/proc/stat` 获取，计算公式为：


```
total_cputime = total_cputime_2 - total_cputime_1
idle_cputime = idle_cputime_2 - idle_cputime_1
percent = ((total_cputime - idle_cputime) / total_cputime) * 100
```

即对总 cpu 时间和空闲 cpu 时间进程分段采样(采样的时间间隔为 0.1 秒)，然后再求差值。


**注：** 所有接口仅在 Ubuntu 环境下测试通过。


## Linux `ps -aux` 命令说明

该命令用于列出系统中所有的进程。`-a` 表示列出所有进程，不区分用户；`-u` 表示以进程属主为主的格式来显示程序状况；`-x` 表示不去分前台还是后台进程。

Linux 上的进程包含 5 种状态:

- 1. 运行(正在运行或在运行队列中等待)
- 2. 中断(休眠中, 受阻, 在等待某个条件的形成或接受到信号)
- 3. 不可中断(收到信号不唤醒和不可运行, 进程必须等待直到有中断发生)
- 4. 僵死(进程已终止, 但进程描述符存在, 等待父进程清理)
- 5. 停止(进程收到 SIGSTOP, SIGSTP, SIGTIN, SIGTOU 信号后停止运行)

`ps` 工具对应 5 种状态的状态码（在 stat 列显示）:

- D: 不可中断 uninterruptible sleep (usually IO)
- R: 运行 runnable (on run queue)
- S: 中断 sleeping
- T: 停止 traced or stopped
- Z: 僵死 a defunct (”zombie”) process

`ps` 工具还有其他的进程状态码：

- W： 进入内存交换（从内核2.6开始无效）
- X： 死掉的进程（很少见）
- <： 高优先级
- n： 低优先级
- s： 包含子进程
- +： 位于后台的进程组

`ps -aux` 命令列出进程的各列的含义如下

- USER: 进程的拥有者
- PID: 进程的 pid
- %CPU: 占用的 CPU 使用率
- %MEM: 占用的 MEM 使用率
- VSZ: 占用的虚拟大小（KB）
- RSS: 占用的固定内存大小（KB）（驻留中页的数量）
- TTY: 进程继承自哪个终端，若无终端（守护进程）则为？
- STAT: 该进程的状态
- START: 进程运行的开始时间
- TIME: 进程实际执行的时间
- COMMAND: 进程执行的命令


## 应用示例

利用 pps 模块写了一个简单的示例，在 example 目录中，即 watchpmc.py。该示例监控指定进程的内存和 CPU 占用，当进程的内存占用超出指定阀值并且总的内存和 CPU 占用超过 90% 时就杀掉该进程。


## 版本

v0.1: 2016-07-09
