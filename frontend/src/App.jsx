import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/public/Home'
import Login from './pages/public/Login'
import Register from './pages/public/Register'
import CarDetails from './pages/public/CarDetails'
import Catalog from './pages/public/Catalog'
import Test from './pages/user/Test'
import Profile from './pages/user/Profile'
import Recommendations from './pages/user/Recommendations'
import Activity from './pages/user/Activity'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminUsers from './pages/admin/Users'
import ProtectedRoute from './routes/ProtectedRoute'
import AdminRoute from './routes/AdminRoute'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/cars/:id" element={<CarDetails />} />
        <Route path="/test" element={<ProtectedRoute><Test /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
        <Route path="/activity" element={<ProtectedRoute><Activity /></ProtectedRoute>} />
        <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
        <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
      </Route>
    </Routes>
  )
}

export default App
