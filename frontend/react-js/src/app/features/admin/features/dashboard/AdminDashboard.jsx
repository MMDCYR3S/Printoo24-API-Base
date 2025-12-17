const DashboardPage = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">داشبورد مدیریت</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* کارت‌های آماری نمونه */}
        <div className="stat bg-base-100 shadow rounded-box">
          <div className="stat-title">فروش کل</div>
          <div className="stat-value text-primary">25.6M</div>
          <div className="stat-desc">21% بیشتر از ماه قبل</div>
        </div>
        
        <div className="stat bg-base-100 shadow rounded-box">
          <div className="stat-title">کاربران جدید</div>
          <div className="stat-value text-secondary">4,200</div>
          <div className="stat-desc">↗︎ 400 (22%)</div>
        </div>

        <div className="stat bg-base-100 shadow rounded-box">
          <div className="stat-title">سفارشات باز</div>
          <div className="stat-value">1,200</div>
          <div className="stat-desc">↘︎ 90 (14%)</div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;