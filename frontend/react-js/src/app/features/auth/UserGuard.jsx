import { Navigate, Outlet } from 'react-router-dom';

const UserGuard = () => {
  const token = localStorage.getItem('accessToken');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default UserGuard;