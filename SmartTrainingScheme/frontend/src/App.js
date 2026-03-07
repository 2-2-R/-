import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, Map, AlertTriangle, BookOpen, Layers, 
  Calendar, ChevronRight, Loader2, Filter, PieChart 
} from 'lucide-react';

/**
 * OBE 权重 UI 配置
 * 用于根据后端返回的 H/M/L 字符渲染对应的颜色深度
 */
const WEIGHT_UI = {
  'H': { color: 'bg-indigo-600', label: '强支撑 (High)', score: 0.5 },
  'M': { color: 'bg-indigo-400', label: '中支撑 (Medium)', score: 0.3 },
  'L': { color: 'bg-indigo-200', label: '弱支撑 (Low)', score: 0.1 },
};

export default function App() {
  const [activeTab, setActiveTab] = useState('heatmap');
  const [filterCategory, setFilterCategory] = useState('全部');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 核心数据状态
  const [data, setData] = useState({ 
    major: "", 
    requirements: [], 
    courses: [] 
  });

  // --- 1. 获取后端聚合数据 ---
  useEffect(() => {
    const fetchOBEData = async () => {
      try {
        setLoading(true);
        // 注意：这里的 URL 必须匹配你 backend/api/urls.py 中的配置
        const response = await fetch('http://127.0.0.1:8000/api/visualize/');
        if (!response.ok) throw new Error('后端接口响应异常，请检查 Django 服务是否启动');
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchOBEData();
  }, []);

  // --- 2. 业务逻辑计算 ---
  const categories = useMemo(() => ['全部', ...new Set(data.courses.map(c => c.category))], [data.courses]);
  
  const filteredCourses = useMemo(() => {
    const list = filterCategory === '全部' 
      ? data.courses 
      : data.courses.filter(c => c.category === filterCategory);
    // 默认按建议学期排序
    return [...list].sort((a, b) => a.semester - b.semester);
  }, [filterCategory, data.courses]);

  // 先修逻辑自检：如果先修课学期 >= 本课学期，则判定为逻辑错误
  const checkLogic = (course) => {
    if (!course.prereqs || course.prereqs.length === 0) return { ok: true };
    const errors = [];
    course.prereqs.forEach(pCode => {
      const pre = data.courses.find(c => c.code === pCode);
      if (pre && pre.semester >= course.semester) {
        errors.push(`先修课 ${pre.name}(第${pre.semester}学期) 不应晚于/等于本课(第${course.semester}学期)`);
      }
    });
    return errors.length > 0 ? { ok: false, errors } : { ok: true };
  };

  // --- 3. UI 渲染逻辑 ---
  if (loading) return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-slate-50">
      <Loader2 className="animate-spin text-indigo-600 mb-4" size={48} />
      <p className="text-slate-500 font-bold tracking-widest animate-pulse">正在解析数据库中的 OBE 矩阵...</p>
    </div>
  );

  if (error) return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-red-50 p-10">
      <AlertTriangle className="text-red-500 mb-4" size={48} />
      <h2 className="text-xl font-bold text-red-700">前后端连接失败</h2>
      <p className="text-red-500 mt-2">{error}</p>
      <button 
        onClick={() => window.location.reload()}
        className="mt-6 px-6 py-2 bg-red-600 text-white rounded-xl font-bold"
      >
        重试连接
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans">
      {/* 顶部导航 */}
      <header className="bg-white/80 backdrop-blur-md border-b sticky top-0 z-50 px-8 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-xl text-white shadow-lg">
            <BarChart3 size={24} />
          </div>
          <div>
            <h1 className="text-xl font-black">{data.major || '未识别专业'}</h1>
            <p className="text-[10px] text-slate-400 font-bold tracking-[0.2em] uppercase">OBE Intelligent Dashboard</p>
          </div>
        </div>
        <div className="flex bg-slate-100 p-1 rounded-2xl border">
          <button 
            onClick={() => setActiveTab('heatmap')}
            className={`px-6 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'heatmap' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
          >
            支撑热力图
          </button>
          <button 
            onClick={() => setActiveTab('logic')}
            className={`px-6 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'logic' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
          >
            逻辑自检
          </button>
        </div>
      </header>

      <main className="p-8 max-w-[1600px] mx-auto">
        {/* 指标看板 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: '课程总数', value: data.courses.length, icon: BookOpen, color: 'text-blue-600' },
            { label: '毕业要求', value: data.requirements.length, icon: Layers, color: 'text-indigo-600' },
            { label: '时序风险', value: data.courses.filter(c => !checkLogic(c).ok).length, icon: AlertTriangle, color: 'text-red-600' },
            { label: '总计学分', value: data.courses.reduce((acc, c) => acc + c.credits, 0), icon: PieChart, color: 'text-emerald-600' },
          ].map((s, i) => (
            <div key={i} className="bg-white p-6 rounded-3xl border shadow-sm hover:shadow-md transition-all group">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-slate-400 text-[10px] font-black uppercase mb-1">{s.label}</p>
                  <p className={`text-3xl font-black ${s.color}`}>{s.value}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-2xl group-hover:scale-110 transition-transform">
                  <s.icon size={24} className="text-slate-400" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 筛选工具 */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
          {categories.map(cat => (
            <button 
              key={cat} 
              onClick={() => setFilterCategory(cat)}
              className={`px-4 py-1.5 rounded-full text-xs font-bold border transition-all whitespace-nowrap ${filterCategory === cat ? 'bg-indigo-600 border-indigo-600 text-white shadow-md' : 'bg-white text-slate-500 hover:border-indigo-300'}`}
            >
              {cat}
            </button>
          ))}
        </div>

        {activeTab === 'heatmap' ? (
          /* 视图 A: OBE 支撑热力图 */
          <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden animate-in fade-in duration-700">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-slate-50/50 text-slate-400">
                    <th className="p-5 border-b border-r text-left text-xs font-black uppercase sticky left-0 bg-white z-20 w-64 shadow-[2px_0_10px_rgba(0,0,0,0.02)]">课程名称 / 详情</th>
                    {data.requirements.map(req => (
                      <th key={req.id} className="p-4 border-b text-center text-[10px] font-black min-w-[70px]">REQ {req.id}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredCourses.map((course, idx) => (
                    <tr key={idx} className="group hover:bg-slate-50/80">
                      <td className="p-5 border-b border-r sticky left-0 bg-white group-hover:bg-slate-50 z-10 shadow-[2px_0_10px_rgba(0,0,0,0.02)]">
                        <div className="flex flex-col">
                          <span className="text-sm font-black text-slate-800 leading-tight mb-1 truncate w-52" title={course.name}>{course.name}</span>
                          <span className="text-[9px] font-mono text-slate-400 uppercase tracking-tighter">{course.code} | 第{course.semester}学期</span>
                        </div>
                      </td>
                      {data.requirements.map(req => {
                        const sup = course.supports?.find(s => s.req === req.id);
                        const ui = sup ? WEIGHT_UI[sup.level] : null;
                        return (
                          <td key={req.id} className="p-2 border-b text-center">
                            {ui ? (
                              <div className={`w-11 h-11 mx-auto rounded-2xl ${ui.color} flex items-center justify-center text-white text-[11px] font-black shadow-inner transform transition-all hover:scale-110 cursor-help group/item relative`}>
                                {sup.level}
                                <div className="absolute bottom-full mb-3 hidden group-hover/item:block bg-slate-900 text-white p-3 rounded-xl text-[10px] w-32 z-50 shadow-2xl animate-in slide-in-from-bottom-1">
                                  <p className="font-bold border-b border-slate-700 pb-1 mb-1">{ui.label}</p>
                                  <p className="text-slate-400">关联毕业要求 {req.id}</p>
                                </div>
                              </div>
                            ) : (
                              <div className="w-11 h-11 mx-auto rounded-2xl bg-slate-50/50 border border-dashed border-slate-100 flex items-center justify-center text-slate-200">-</div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="p-8 bg-slate-50/50 border-t flex flex-wrap justify-center gap-10">
              {Object.entries(WEIGHT_UI).map(([key, val]) => (
                <div key={key} className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded-lg ${val.color} shadow-sm shadow-indigo-200`}></div>
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{val.label} ({key})</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* 视图 B: 先修逻辑检测视图 */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in slide-in-from-right-4 duration-500">
            {filteredCourses.map((course, idx) => {
              const res = checkLogic(course);
              return (
                <div key={idx} className={`bg-white p-6 rounded-3xl border-2 transition-all ${res.ok ? 'border-slate-100 hover:border-indigo-100' : 'border-red-200 bg-red-50/30 shadow-lg shadow-red-100'}`}>
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex gap-4">
                      <div className={`p-3 rounded-2xl ${res.ok ? 'bg-indigo-50 text-indigo-600' : 'bg-red-100 text-red-600'}`}>
                        <Calendar size={24} />
                      </div>
                      <div>
                        <h3 className="text-lg font-black text-slate-800 mb-1 leading-tight">{course.name}</h3>
                        <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">{course.category}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">建议学期</p>
                      <p className={`text-2xl font-black ${res.ok ? 'text-slate-700' : 'text-red-600'}`}>第 {course.semester} 学期</p>
                    </div>
                  </div>

                  {!res.ok && (
                    <div className="mb-4 bg-red-100/50 border border-red-200 p-4 rounded-2xl text-red-700 animate-in shake duration-500">
                      <p className="text-xs font-black flex items-center gap-2 mb-2 uppercase tracking-wider">
                        <AlertTriangle size={14} /> 开课时序冲突警告
                      </p>
                      {res.errors.map((err, i) => (
                        <p key={i} className="text-xs italic leading-relaxed opacity-90">- {err}</p>
                      ))}
                    </div>
                  )}

                  <div className="pt-4 border-t border-slate-100 flex items-center gap-3 overflow-x-auto pb-1 scrollbar-hide">
                    <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest whitespace-nowrap">逻辑链:</span>
                    {course.prereqs && course.prereqs.length > 0 ? course.prereqs.map(p => (
                      <div key={p} className="flex items-center gap-2">
                         <span className="px-3 py-1 bg-slate-100 rounded-lg text-[10px] font-mono text-slate-500 whitespace-nowrap border border-slate-200">{p}</span>
                         <ChevronRight size={12} className="text-slate-300" />
                      </div>
                    )) : <span className="text-[10px] italic text-slate-300">无先修要求</span>}
                    {course.prereqs?.length > 0 && <span className="px-3 py-1 bg-indigo-600 rounded-lg text-[10px] font-bold text-white whitespace-nowrap shadow-md">本课</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      <footer className="p-12 text-center text-[10px] font-black text-slate-300 uppercase tracking-[0.4em] leading-loose">
        &copy; 2024 OBE Smart Training Scheme Visualization System<br/>
        Data Driven by Django & React
      </footer>
    </div>
  );
}