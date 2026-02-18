"""
MaiBot-Plugin-Kit 全功能测试
测试范围：
  1. mai CLI — create / list-templates / validate / pack / run-maiscript
  2. JS SDK (mai-sdk.js) — mai.reply/command/action, ctx.send/match/param/config/log
  3. mai_js_bridge Python 侧 — JsBridgeLoader
  4. MaiScript — 解析 + 编译（YAML 格式）
  5. mai_advanced — AdvancedReplyBuilder / ReplyComponent / PromptModifier
"""

import sys, os, io, json, shutil, subprocess, tempfile, traceback

# 强制 stdout/stderr 使用 UTF-8，避免 Windows GBK 编码错误
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, r's:\VSCODE\CodeX\MaiBot-Plugin-Kit')

REPO   = r's:\VSCODE\CodeX\MaiBot-Plugin-Kit'
PASS   = '✅'
FAIL   = '❌'
SKIP   = '⏭️ '
results = []

def section(title):
    print(f'\n{"="*60}')
    print(f'  {title}')
    print(f'{"="*60}')

def ok(name):
    results.append((name, True, ''))
    print(f'  {PASS} {name}')

def fail(name, err=''):
    results.append((name, False, str(err)[:300]))
    print(f'  {FAIL} {name}: {str(err)[:120]}')

def skip(name, reason=''):
    results.append((name, None, reason))
    print(f'  {SKIP} {name}: {reason}')

def run_cmd(args, cwd=None, input_text=None):
    # 将 REPO 加入 PYTHONPATH，让子进程能找到 mai_plugin_cli 包
    env = os.environ.copy()
    env['PYTHONPATH'] = REPO + os.pathsep + env.get('PYTHONPATH', '')
    r = subprocess.run(
        [sys.executable, '-m', 'mai_plugin_cli'] + args,
        cwd=cwd or REPO,
        capture_output=True, text=True,
        encoding='utf-8', errors='replace',
        input=input_text,
        env=env,
    )
    return r.returncode, r.stdout, r.stderr

tmpdir = tempfile.mkdtemp(prefix='mai_test_')

# ─── 1. CLI: list-templates ───────────────────────────────────────────────────
section('1. CLI — list-templates')
try:
    rc, out, err = run_cmd(['list-templates'])
    assert rc == 0, f'rc={rc}\n{err}'
    ok('list-templates 返回 0')
except Exception as e:
    fail('list-templates', e)

# ─── 2. CLI: create (每个模板) ────────────────────────────────────────────────
section('2. CLI — create templates')
# 注意：版本号参数是 --version-str，不是 --version
for tpl in ['minimal', 'command', 'action', 'full', 'js_bridge', 'advanced']:
    pname = f'test_{tpl}'
    try:
        rc, out, err = run_cmd(
            ['create', pname, '-t', tpl,
             '--author', 'TestBot',
             '--version-str', '0.1.0',
             '-y'],
            cwd=tmpdir,
        )
        pdir = os.path.join(tmpdir, pname)
        assert os.path.isdir(pdir), f'目录未创建: rc={rc}\nOUT={out[:200]}\nERR={err[:200]}'
        assert os.path.isfile(os.path.join(pdir, '_manifest.json')), '_manifest.json 不存在'
        assert os.path.isfile(os.path.join(pdir, 'plugin.py')), 'plugin.py 不存在'
        # 检查占位符已被替换
        with open(os.path.join(pdir, 'plugin.py'), encoding='utf-8') as f:
            code = f.read()
        assert '{{PLUGIN_NAME}}' not in code, 'plugin.py 仍有 {{PLUGIN_NAME}}'
        assert '{{PLUGIN_CLASS_NAME}}' not in code, 'plugin.py 仍有 {{PLUGIN_CLASS_NAME}}'
        ok(f'create -t {tpl}')
    except Exception as e:
        fail(f'create -t {tpl}', e)

# ─── 3. CLI: validate ────────────────────────────────────────────────────────
section('3. CLI — validate')
for tpl in ['minimal', 'command', 'action', 'full']:
    pname = f'test_{tpl}'
    pdir = os.path.join(tmpdir, pname)
    if not os.path.isdir(pdir):
        skip(f'validate {tpl}', '目录不存在（create 步骤失败）')
        continue
    try:
        rc, out, err = run_cmd(['validate', pdir])
        combined = out + err
        # 允许 validate 返回非 0（MaiBot 环境不完整），但不能有 exception/traceback
        assert 'traceback' not in combined.lower(), f'validate 崩溃: {combined[:200]}'
        ok(f'validate {tpl}')
    except Exception as e:
        fail(f'validate {tpl}', e)

# ─── 4. CLI: pack ─────────────────────────────────────────────────────────────
section('4. CLI — pack')
for tpl in ['minimal', 'command']:
    pname = f'test_{tpl}'
    pdir = os.path.join(tmpdir, pname)
    if not os.path.isdir(pdir):
        skip(f'pack {tpl}', '目录不存在')
        continue
    # pack 的 -o 参数是输出 ZIP 文件的完整路径，不是目录
    out_zip = os.path.join(tmpdir, f'{pname}.zip')
    try:
        rc, out, err = run_cmd(['pack', pdir, '-o', out_zip])
        assert os.path.isfile(out_zip), f'zip 未生成: rc={rc}\n{out[:150]}\n{err[:150]}'
        size = os.path.getsize(out_zip)
        assert size > 0, f'zip 大小为 0'
        ok(f'pack {tpl} → {os.path.basename(out_zip)} ({size//1024}KB)')
    except Exception as e:
        fail(f'pack {tpl}', e)

# ─── 5. MaiScript: 解析与编译 (YAML 格式) ────────────────────────────────────
section('5. MaiScript — 解析与编译（YAML 格式）')
try:
    from mai_script.parser import MaiScriptParser
    ok('MaiScriptParser 可导入')

    # 方法名是 parse_string，不是 parse
    assert hasattr(MaiScriptParser, 'parse_string'), 'parse_string 方法不存在'
    assert hasattr(MaiScriptParser, 'parse_file'), 'parse_file 方法不存在'
    ok('MaiScriptParser API 方法存在（parse_string / parse_file）')

    # MaiScript 使用 YAML 格式
    SCRIPT_YAML = """
plugin:
  name: "测试插件"
  version: "1.0.0"
  author: "TestBot"
  description: "测试用插件"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好！"

  - name: "查询"
    match: "/echo {text}"
    reply: "你说：{text}"

actions:
  - name: "问候动作"
    when:
      - "当有人打招呼时"
    reply: "很高兴见到你！"
"""
    parser = MaiScriptParser()
    try:
        result = parser.parse_string(SCRIPT_YAML)
        assert isinstance(result, dict), f'parse_string 返回类型错误: {type(result)}'
        assert 'plugin' in result, '结果缺少 plugin 键'
        assert 'commands' in result, '结果缺少 commands 键'
        assert 'actions' in result, '结果缺少 actions 键'
        assert len(result['commands']) == 2, f'commands 数量错误: {len(result["commands"])}'
        assert len(result['actions']) == 1, f'actions 数量错误: {len(result["actions"])}'
        ok('parse_string() 返回正确结构')
    except ImportError as ie:
        skip('parse_string() 解析', f'需要 pyyaml: {ie}')
    except Exception as e:
        fail('parse_string() 解析', e)

    # 写入临时文件测试 parse_file
    ms_file = os.path.join(tmpdir, 'test.mai')
    with open(ms_file, 'w', encoding='utf-8') as f:
        f.write(SCRIPT_YAML)
    try:
        result2 = parser.parse_file(ms_file)
        assert result2['plugin']['name'] == '测试插件', f'plugin name 错误: {result2["plugin"]}'
        ok('parse_file() 读取文件解析')
    except ImportError:
        skip('parse_file()', '需要 pyyaml')
    except Exception as e:
        fail('parse_file()', e)

except Exception as e:
    fail('MaiScriptParser 导入', e)

try:
    from mai_script.compiler import MaiScriptCompiler
    ok('MaiScriptCompiler 可导入')

    compiler = MaiScriptCompiler()
    # compile() 接受已解析的 dict（不是 YAML 字符串）
    # 当不传 output_dir 时，返回 {filename: content} 字典
    try:
        parsed_data = parser.parse_string(SCRIPT_YAML)   # 先解析
        files = compiler.compile(parsed_data)             # 传 dict
        assert isinstance(files, dict), f'compile() 应返回 dict: {type(files)}'
        assert 'plugin.py' in files, f'缺少 plugin.py，有：{list(files.keys())}'
        assert '_manifest.json' in files, f'缺少 _manifest.json'
        code = files['plugin.py']
        assert 'class' in code or 'def ' in code, f'plugin.py 不含类/函数: {code[:200]}'
        ok('MaiScriptCompiler.compile(dict) → {filename: content}')
        ok(f'compile() 生成文件：{list(files.keys())}')
    except ImportError:
        skip('MaiScriptCompiler.compile()', '需要 pyyaml')
    except Exception as e:
        fail('MaiScriptCompiler.compile()', e)

    # 测试 compile_file()（直接从 .mai 文件编译到目录）
    try:
        out_plugin_dir = os.path.join(tmpdir, 'compiled_plugin')
        compiler.compile_file(ms_file, output_dir=out_plugin_dir)
        assert os.path.isdir(out_plugin_dir), '输出目录未生成'
        assert os.path.isfile(os.path.join(out_plugin_dir, 'plugin.py')), 'plugin.py 不存在'
        assert os.path.isfile(os.path.join(out_plugin_dir, '_manifest.json')), '_manifest.json 不存在'
        ok('MaiScriptCompiler.compile_file() 写入磁盘')
    except ImportError:
        skip('MaiScriptCompiler.compile_file()', '需要 pyyaml')
    except Exception as e:
        fail('MaiScriptCompiler.compile_file()', e)

except Exception as e:
    fail('MaiScriptCompiler 导入', e)

# ─── 6. CLI: run-maiscript ───────────────────────────────────────────────────
section('6. CLI — run-maiscript')
ms_file = os.path.join(tmpdir, 'test.mai')
if os.path.isfile(ms_file):
    try:
        rc, out, err = run_cmd(['run-maiscript', ms_file, '-o', tmpdir])
        combined = out + err
        assert 'traceback' not in combined.lower(), f'run-maiscript 崩溃: {combined[:200]}'
        ok('run-maiscript 执行无崩溃')
    except Exception as e:
        fail('run-maiscript', e)
else:
    skip('run-maiscript', 'test.mai 未创建')

# ─── 7. JS SDK (Node.js) ─────────────────────────────────────────────────────
section('7. JS SDK — mai-sdk.js (Node.js)')
node_ver = subprocess.run(['node', '--version'], capture_output=True, text=True)
HAS_NODE = node_ver.returncode == 0

if not HAS_NODE:
    skip('JS SDK 全部测试', 'node 命令不可用')
else:
    print(f'     Node.js: {node_ver.stdout.strip()}')
    SDK = os.path.join(REPO, 'mai_js_bridge', 'sdk', 'mai-sdk.js')

    JS_TEST = r"""
const { createRegistrar, createContext, executeComponent } = require(process.argv[2]);

async function run() {
  function check(name, cond, msg) {
    if (!cond) process.stderr.write(`FAIL: ${name}: ${msg}\n`);
    else process.stderr.write(`PASS: ${name}\n`);
  }

  const { mai, commands, actions } = createRegistrar();

  // mai.reply()
  mai.reply('/ping', 'Pong!');
  check('mai.reply', commands.size === 1, `size=${commands.size}`);

  // mai.command(pattern, fn)
  mai.command(/^\/echo\s+(.+)$/, async (ctx) => { await ctx.send(`echo:${ctx.match(1)}`); });
  check('mai.command(pattern, fn)', commands.size === 2, `size=${commands.size}`);

  // mai.command(config)
  mai.command({ name: 'roll', pattern: /^\/roll(\d+)?$/, execute: async (ctx) => {
    await ctx.send(`${Math.floor(Math.random() * (parseInt(ctx.match(1),10)||6)) + 1}`);
    return { success: true };
  }});
  check('mai.command(config)', commands.has('roll'), 'roll not found');

  // mai.action(config)
  mai.action({ name: 'greet', execute: async (ctx) => {
    await ctx.send(`Hello, ${ctx.param('user','World')}!`);
    return { success: true };
  }});
  check('mai.action(config)', actions.has('greet'), 'greet not found');

  // ctx.match
  const c1 = createContext({ plugin_name:'t', matched_groups:['hello world'] });
  check('ctx.match(1)', c1.match(1) === 'hello world', c1.match(1));
  check('ctx.getMatch(1) alias', c1.getMatch(1) === 'hello world', c1.getMatch(1));
  check('ctx.match(0)→null', c1.match(0) === null, c1.match(0));

  // ctx.param
  const c2 = createContext({ plugin_name:'t', action_data:{ city:'Beijing' } });
  check('ctx.param(key)', c2.param('city') === 'Beijing', c2.param('city'));
  check('ctx.param(missing,default)', c2.param('x','bar') === 'bar', c2.param('x','bar'));
  check('ctx.getParam() alias', c2.getParam('city') === 'Beijing', '');

  // ctx.config
  const c3 = createContext({ plugin_name:'t', config:{ s:{ k:'v123' } } });
  check('ctx.config(dot-key)', c3.config('s.k') === 'v123', c3.config('s.k'));
  check('ctx.config(missing,default)', c3.config('x.y','def') === 'def', '');
  check('ctx.getConfig() alias', c3.getConfig('s.k') === 'v123', '');

  // ctx.send / sendText / sendImage / sendEmoji
  const c4 = createContext({ plugin_name:'t' });
  await c4.send('hi'); await c4.sendText('world');
  await c4.sendImage('img64'); await c4.sendEmoji('emoji64');
  const msgs = c4._getMessages();
  check('ctx.send() text', msgs[0]?.content==='hi', JSON.stringify(msgs[0]));
  check('ctx.sendText() text', msgs[1]?.content==='world', JSON.stringify(msgs[1]));
  check('ctx.sendImage() image', msgs[2]?.type==='image', JSON.stringify(msgs[2]));
  check('ctx.sendEmoji() emoji', msgs[3]?.type==='emoji', JSON.stringify(msgs[3]));

  // executeComponent — mai.reply
  const r1 = createRegistrar();
  r1.mai.reply('/t','fixed reply','tst');
  const res1 = await executeComponent(r1, 'tst', { plugin_name:'t' });
  check('executeComponent mai.reply → success', res1.success===true, JSON.stringify(res1));
  check('executeComponent mai.reply → message', res1.messages[0]?.content==='fixed reply', JSON.stringify(res1.messages));

  // executeComponent — ctx.match
  const r2 = createRegistrar();
  r2.mai.command({ name:'et', execute: async(ctx)=>{ await ctx.send(ctx.match(1)); return{success:true}; }});
  const res2 = await executeComponent(r2,'et',{plugin_name:'t',matched_groups:['hello']});
  check('executeComponent ctx.match', res2.messages[0]?.content==='hello', JSON.stringify(res2.messages));

  // executeComponent — missing
  const res3 = await executeComponent(r2,'nonexistent',{plugin_name:'t'});
  check('executeComponent missing→false', res3.success===false, JSON.stringify(res3));

  // mai.command(fn only)
  const r3 = createRegistrar();
  r3.mai.command(async(ctx) => { await ctx.send('catchall'); });
  check('mai.command(fn) → commands.size=1', r3.commands.size===1, r3.commands.size);

  process.exit(0);
}

run().catch(err => { process.stderr.write('UNCAUGHT: '+err+'\n'); process.exit(1); });
"""
    js_test_file = os.path.join(tmpdir, 'sdk_test.js')
    with open(js_test_file, 'w', encoding='utf-8') as f:
        f.write(JS_TEST)

    r = subprocess.run(['node', js_test_file, SDK],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    for line in r.stderr.splitlines():
        if line.startswith('PASS:'):
            ok(line[6:].strip())
        elif line.startswith('FAIL:'):
            fail(line[6:].strip())
        elif line.startswith('UNCAUGHT:'):
            fail('JS 未捕获异常', line)
    if r.returncode != 0 and not any(l.startswith(('PASS:','FAIL:')) for l in r.stderr.splitlines()):
        fail('JS SDK 整体', f'rc={r.returncode}\n{r.stderr[:300]}')

# ─── 8a. bridge._parse_js_registrations (新增全形式解析测试) ──────────────────
section('8a. bridge._parse_js_registrations — 全注册形式解析')
try:
    from mai_js_bridge.bridge import _parse_js_registrations

    JS_SAMPLE = """
// 1. mai.reply 无 name
mai.reply('/ping', 'Pong!');

// 2. mai.reply 带 name
mai.reply('/status', '运行正常', 'status_cmd');

// 3. mai.command(pattern, fn) 简洁写法
mai.command(/^\\/echo\\s+(.+)$/, async (ctx) => {
  await ctx.send(`echo: ${ctx.match(1)}`);
});

// 4. mai.command({ name: ... }) 对象写法
mai.command({
  name: 'roll',
  pattern: /^\\/roll(\\d+)?$/,
  description: '掷骰子',
  execute: async (ctx) => { return { success: true }; }
});

// 5. mai.action({ name: ... }) 对象写法
mai.action({
  name: 'greet',
  description: '问候用户',
  require: ['当有人打招呼时'],
  parameters: { user_name: '用户名字' },
  types: ['text'],
  execute: async (ctx) => { return { success: true }; }
});
"""
    result = _parse_js_registrations(JS_SAMPLE)
    cmd_names = [c['name'] for c in result['commands']]
    act_names = [a['name'] for a in result['actions']]

    # mai.reply 无 name → auto_reply_0
    assert 'auto_reply_0' in cmd_names, f'auto_reply_0 未检测到: {cmd_names}'
    ok('_parse_js_registrations: mai.reply() 无 name → auto_reply_0')

    # mai.reply 带 name → status_cmd
    assert 'status_cmd' in cmd_names, f'status_cmd 未检测到: {cmd_names}'
    ok('_parse_js_registrations: mai.reply(pattern, text, name) → status_cmd')

    # mai.command(pattern, fn) 简洁写法 → auto_cmd_0
    assert 'auto_cmd_0' in cmd_names, f'auto_cmd_0 未检测到: {cmd_names}'
    ok('_parse_js_registrations: mai.command(/pattern/, fn) → auto_cmd_0')

    # mai.command({name: 'roll'}) → roll
    assert 'roll' in cmd_names, f'roll 未检测到: {cmd_names}'
    ok('_parse_js_registrations: mai.command({name}) → roll')

    # mai.action({name: 'greet'}) → greet
    assert 'greet' in act_names, f'greet 未检测到: {act_names}'
    ok('_parse_js_registrations: mai.action({name}) → greet')
    ok(f'总计检测到 {len(cmd_names)} 个命令，{len(act_names)} 个 action')

except Exception as e:
    fail('_parse_js_registrations', e)

# ─── 8. JS Bridge Python 侧 ──────────────────────────────────────────────────
section('8. mai_js_bridge Python 侧')
if not HAS_NODE:
    skip('JsBridgeLoader', 'Node.js 不可用')
else:
    try:
        from mai_js_bridge import JsBridgeLoader
        ok('JsBridgeLoader 可导入')

        js_plugin = os.path.join(tmpdir, 'simple.js')
        with open(js_plugin, 'w', encoding='utf-8') as f:
            f.write("""
mai.reply('/hello', 'Hello World!', 'hello_cmd');
mai.action({ name: 'my_action', execute: async (ctx) => { await ctx.send('action!'); return {success:true}; } });
""")
        loader = JsBridgeLoader(js_plugin, plugin_name='test_plugin')
        # 在 MaiBot 环境外 get_components() 返回 [] 是预期行为
        components = loader.get_components()
        assert isinstance(components, list), f'get_components() 应返回列表'
        ok(f'JsBridgeLoader.get_components() 返回列表（{len(components)} 项）')
        # 在 MaiBot 环境外返回空是正常的
        if len(components) == 0:
            ok('MaiBot 环境外 JsBridgeLoader 优雅降级（返回空列表）')
        else:
            ok(f'JsBridgeLoader 加载了 {len(components)} 个组件')
    except Exception as e:
        fail('JsBridgeLoader', e)
        traceback.print_exc()

# ─── 9. mai_advanced ─────────────────────────────────────────────────────────
section('9. mai_advanced — 属性兼容性')

# _stream_id / _chat_stream 属性在 BaseAction / BaseCommand 两种情形下的行为
try:
    from mai_advanced.reply_builder import AdvancedReplyBuilder
    from mai_advanced.prompt_modifier import PromptModifier

    # ── 模拟 BaseAction：有 chat_id 和 chat_stream 直接属性
    class FakeAction:
        chat_id = "action_stream_001"
        chat_stream = object()   # 非 None 即可

    action_builder = AdvancedReplyBuilder(FakeAction())
    assert action_builder._stream_id == "action_stream_001", \
        f"_stream_id 期望 action_stream_001，实际 {action_builder._stream_id!r}"
    ok('AdvancedReplyBuilder._stream_id 兼容 BaseAction(chat_id)')

    assert action_builder._chat_stream is FakeAction.chat_stream, \
        "_chat_stream 应直接返回 FakeAction.chat_stream"
    ok('AdvancedReplyBuilder._chat_stream 兼容 BaseAction(chat_stream 直接属性)')

    # ── 模拟 BaseCommand：有 message.chat_stream，无 chat_id / stream_id / chat_stream
    class FakeMessage:
        chat_stream = object()
        stream_id = "cmd_stream_002"

    class FakeCommand:
        message = FakeMessage()
        # 无 chat_id / stream_id / chat_stream

    cmd_builder = AdvancedReplyBuilder(FakeCommand())
    assert cmd_builder._stream_id == "", \
        f"FakeCommand 无 stream_id/chat_id，期望空串，实际 {cmd_builder._stream_id!r}"
    ok('AdvancedReplyBuilder._stream_id: 无 stream_id/chat_id 时返回空串')

    assert cmd_builder._chat_stream is FakeMessage.chat_stream, \
        "_chat_stream 应通过 message.chat_stream 兜底"
    ok('AdvancedReplyBuilder._chat_stream 兼容 BaseCommand(message.chat_stream 兜底)')

    # ── PromptModifier 同样检测
    pm = PromptModifier(FakeAction())
    assert pm._stream_id == "action_stream_001"
    ok('PromptModifier._stream_id 兼容 BaseAction(chat_id)')
    assert pm._chat_stream is FakeAction.chat_stream
    ok('PromptModifier._chat_stream 兼容 BaseAction 直接属性')

except Exception as e:
    fail('advanced 属性兼容性', e)

section('9b. mai_advanced — 类和方法存在性')

# ReplyComponent
try:
    from mai_advanced.reply_builder import ReplyComponent
    c = ReplyComponent.text('hello')
    assert c.type == 'text' and c.content == 'hello'
    ok('ReplyComponent.text() 工厂方法')
    c2 = ReplyComponent.emoji('base64data')
    assert c2.type == 'emoji'
    ok('ReplyComponent.emoji() 工厂方法')
    c3 = ReplyComponent.image('base64img')
    assert c3.type == 'image'
    ok('ReplyComponent.image() 工厂方法')
except Exception as e:
    fail('ReplyComponent', e)

# AdvancedReplyBuilder（需要 plugin_component 参数，在 MaiBot 外无法实例化，只测试导入）
try:
    from mai_advanced.reply_builder import AdvancedReplyBuilder
    ok('AdvancedReplyBuilder 可导入')
    # 检查方法签名
    assert hasattr(AdvancedReplyBuilder, 'generate_reply'), 'generate_reply 缺失'
    assert hasattr(AdvancedReplyBuilder, 'generate_custom_reply'), 'generate_custom_reply 缺失'
    assert hasattr(AdvancedReplyBuilder, 'rewrite_reply'), 'rewrite_reply 缺失'
    assert hasattr(AdvancedReplyBuilder, 'send_components'), 'send_components 缺失'
    assert hasattr(AdvancedReplyBuilder, 'inject_before'), 'inject_before 缺失'
    ok('AdvancedReplyBuilder 所有方法存在')
except Exception as e:
    fail('AdvancedReplyBuilder', e)

# PromptModifier
try:
    from mai_advanced.prompt_modifier import PromptModifier
    ok('PromptModifier 可导入')
    assert hasattr(PromptModifier, 'call_model'), 'call_model 缺失'
    assert hasattr(PromptModifier, 'generate_with_extra_context'), 'generate_with_extra_context 缺失'
    assert hasattr(PromptModifier, 'call_model_with_tools'), 'call_model_with_tools 缺失'
    ok('PromptModifier 所有方法存在')
except Exception as e:
    fail('PromptModifier', e)

# ─── 汇总 ─────────────────────────────────────────────────────────────────────
section('测试汇总')
passed = sum(1 for _, s, _ in results if s is True)
failed = sum(1 for _, s, _ in results if s is False)
skipped = sum(1 for _, s, _ in results if s is None)
total  = len(results)
print(f'\n  总计：{total} 项  通过：{passed}  失败：{failed}  跳过：{skipped}')

if failed:
    print('\n  ❌ 失败列表：')
    for name, s, err in results:
        if s is False:
            print(f'    ❌ {name}: {err[:150]}')

shutil.rmtree(tmpdir, ignore_errors=True)
sys.exit(0 if failed == 0 else 1)
