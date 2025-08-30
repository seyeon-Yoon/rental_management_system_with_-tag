import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  InputAdornment,
  Alert,
  Pagination,
  IconButton,
  Menu,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add,
  Search,
  Edit,
  Delete,
  MoreVert,
  CheckCircle,
  Schedule,
  Build,
  Block,
  Category as CategoryIcon,
  Inventory,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { itemService } from '../../services/itemService';
import { categoryService } from '../../services/categoryService';
import { Item, Category } from '../../types';
import Loading from '../../components/common/Loading';
import ErrorMessage from '../../components/common/ErrorMessage';

interface ItemFormData {
  name: string;
  description: string;
  category_id: number | '';
  serial_number: string;
  status: 'AVAILABLE' | 'MAINTENANCE';
  metadata: Record<string, any>;
}

const ItemManagement: React.FC = () => {
  const queryClient = useQueryClient();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | ''>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [page, setPage] = useState(1);
  
  // 다이얼로그 상태
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
  // 메뉴 상태
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [menuItem, setMenuItem] = useState<Item | null>(null);
  
  // 폼 상태
  const [formData, setFormData] = useState<ItemFormData>({
    name: '',
    description: '',
    category_id: '',
    serial_number: '',
    status: 'AVAILABLE',
    metadata: {},
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const itemsPerPage = 12;

  // 카테고리 목록 조회
  const { data: categoriesResponse } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryService.getCategories({ limit: 100 }),
  });

  // 품목 목록 조회
  const {
    data: itemsResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['admin-items', searchTerm, selectedCategory, selectedStatus, page],
    queryFn: () => 
      itemService.getItems({
        page,
        limit: itemsPerPage,
        search: searchTerm || undefined,
        category_id: selectedCategory || undefined,
        status: selectedStatus || undefined,
      }),
  });

  // 품목 생성 Mutation
  const createItemMutation = useMutation({
    mutationFn: (data: Partial<Item>) => itemService.createItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-items'] });
      queryClient.invalidateQueries({ queryKey: ['item-statistics'] });
      handleFormClose();
    },
  });

  // 품목 수정 Mutation
  const updateItemMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Item> }) =>
      itemService.updateItem(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-items'] });
      handleFormClose();
    },
  });

  // 품목 삭제 Mutation
  const deleteItemMutation = useMutation({
    mutationFn: (id: number) => itemService.deleteItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-items'] });
      queryClient.invalidateQueries({ queryKey: ['item-statistics'] });
      setDeleteDialogOpen(false);
      setSelectedItem(null);
    },
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return <CheckCircle color="success" />;
      case 'RESERVED':
        return <Schedule color="warning" />;
      case 'RENTED':
        return <Block color="error" />;
      case 'MAINTENANCE':
        return <Build color="info" />;
      default:
        return undefined;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return '대여 가능';
      case 'RESERVED':
        return '예약됨';
      case 'RENTED':
        return '대여 중';
      case 'MAINTENANCE':
        return '정비 중';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return 'success';
      case 'RESERVED':
        return 'warning';
      case 'RENTED':
        return 'error';
      case 'MAINTENANCE':
        return 'info';
      default:
        return 'default';
    }
  };

  const handleFormOpen = (item?: Item) => {
    if (item) {
      setIsEditing(true);
      setSelectedItem(item);
      setFormData({
        name: item.name,
        description: item.description || '',
        category_id: item.category_id,
        serial_number: item.serial_number,
        status: item.status === 'RESERVED' || item.status === 'RENTED' ? 'AVAILABLE' : item.status as 'AVAILABLE' | 'MAINTENANCE',
        metadata: item.metadata || {},
      });
    } else {
      setIsEditing(false);
      setSelectedItem(null);
      setFormData({
        name: '',
        description: '',
        category_id: '',
        serial_number: '',
        status: 'AVAILABLE',
        metadata: {},
      });
    }
    setFormErrors({});
    setFormDialogOpen(true);
  };

  const handleFormClose = () => {
    setFormDialogOpen(false);
    setSelectedItem(null);
    setFormData({
      name: '',
      description: '',
      category_id: '',
      serial_number: '',
      status: 'AVAILABLE',
      metadata: {},
    });
    setFormErrors({});
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = '품목명을 입력해주세요.';
    }

    if (!formData.category_id) {
      errors.category_id = '카테고리를 선택해주세요.';
    }

    if (!formData.serial_number.trim()) {
      errors.serial_number = '일련번호를 입력해주세요.';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleFormSubmit = () => {
    if (!validateForm()) return;

    const submitData = {
      ...formData,
      category_id: formData.category_id as number,
    };

    if (isEditing && selectedItem) {
      updateItemMutation.mutate({ id: selectedItem.id, data: submitData });
    } else {
      createItemMutation.mutate(submitData);
    }
  };

  const handleDeleteClick = (item: Item) => {
    setSelectedItem(item);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedItem) {
      deleteItemMutation.mutate(selectedItem.id);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, item: Item) => {
    setMenuAnchorEl(event.currentTarget);
    setMenuItem(item);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setMenuItem(null);
  };

  const categories = categoriesResponse?.items || [];
  const items = itemsResponse?.items || [];
  const totalPages = Math.ceil((itemsResponse?.total || 0) / itemsPerPage);

  if (isLoading && page === 1) {
    return <Loading message="품목 목록을 불러오는 중..." fullHeight />;
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* 페이지 헤더 */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
            품목 관리
          </Typography>
          <Typography variant="body1" color="text.secondary">
            대여 품목을 등록하고 관리하세요.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleFormOpen()}
          size="large"
        >
          품목 등록
        </Button>
      </Box>

      {/* 검색 및 필터 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="품목명 또는 일련번호로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>카테고리</InputLabel>
                <Select
                  value={selectedCategory}
                  label="카테고리"
                  onChange={(e) => setSelectedCategory(e.target.value as number | '')}
                >
                  <MenuItem value="">전체 카테고리</MenuItem>
                  {categories.map((category: Category) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>상태</InputLabel>
                <Select
                  value={selectedStatus}
                  label="상태"
                  onChange={(e) => setSelectedStatus(e.target.value)}
                >
                  <MenuItem value="">전체 상태</MenuItem>
                  <MenuItem value="AVAILABLE">대여 가능</MenuItem>
                  <MenuItem value="RESERVED">예약됨</MenuItem>
                  <MenuItem value="RENTED">대여 중</MenuItem>
                  <MenuItem value="MAINTENANCE">정비 중</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 에러 처리 */}
      {error && (
        <ErrorMessage
          title="품목을 불러오는데 실패했습니다"
          message={error.message}
          onRetry={() => refetch()}
        />
      )}

      {/* 품목 목록 */}
      {items.length === 0 && !isLoading ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Inventory sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            조건에 맞는 품목이 없습니다
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {items.map((item: Item) => (
            <Grid item xs={12} sm={6} lg={4} key={item.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h3">
                      {item.name}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, item)}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CategoryIcon sx={{ fontSize: 16, mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {item.category?.name}
                    </Typography>
                  </Box>

                  {item.description && (
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {item.description}
                    </Typography>
                  )}

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      일련번호:
                    </Typography>
                    <Typography variant="body2" fontFamily="monospace">
                      {item.serial_number}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={getStatusText(item.status)}
                      color={getStatusColor(item.status) as any}
                      size="small"
                      icon={getStatusIcon(item.status)}
                    />
                  </Box>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => handleFormOpen(item)}
                    disabled={item.status === 'RENTED'}
                  >
                    수정
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<Delete />}
                    onClick={() => handleDeleteClick(item)}
                    disabled={item.status === 'RESERVED' || item.status === 'RENTED'}
                  >
                    삭제
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, value) => setPage(value)}
            color="primary"
          />
        </Box>
      )}

      {/* 메뉴 */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => { handleFormOpen(menuItem!); handleMenuClose(); }}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>수정</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => { handleDeleteClick(menuItem!); handleMenuClose(); }}
          disabled={menuItem?.status === 'RESERVED' || menuItem?.status === 'RENTED'}
        >
          <ListItemIcon>
            <Delete fontSize="small" />
          </ListItemIcon>
          <ListItemText>삭제</ListItemText>
        </MenuItem>
      </Menu>

      {/* 품목 등록/수정 다이얼로그 */}
      <Dialog
        open={formDialogOpen}
        onClose={handleFormClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {isEditing ? '품목 수정' : '품목 등록'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="품목명"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              error={!!formErrors.name}
              helperText={formErrors.name}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth sx={{ mb: 2 }} error={!!formErrors.category_id}>
              <InputLabel>카테고리</InputLabel>
              <Select
                value={formData.category_id}
                label="카테고리"
                onChange={(e) => setFormData(prev => ({ ...prev, category_id: e.target.value as number }))}
              >
                {categories.map((category: Category) => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))}
              </Select>
              {formErrors.category_id && (
                <Typography variant="caption" color="error">
                  {formErrors.category_id}
                </Typography>
              )}
            </FormControl>

            <TextField
              fullWidth
              label="일련번호"
              value={formData.serial_number}
              onChange={(e) => setFormData(prev => ({ ...prev, serial_number: e.target.value }))}
              error={!!formErrors.serial_number}
              helperText={formErrors.serial_number || '품목을 구분하는 고유 번호를 입력하세요'}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>상태</InputLabel>
              <Select
                value={formData.status}
                label="상태"
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as 'AVAILABLE' | 'MAINTENANCE' }))}
              >
                <MenuItem value="AVAILABLE">대여 가능</MenuItem>
                <MenuItem value="MAINTENANCE">정비 중</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="설명"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="품목에 대한 자세한 설명을 입력하세요 (선택사항)"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleFormClose}>
            취소
          </Button>
          <Button
            onClick={handleFormSubmit}
            variant="contained"
            disabled={createItemMutation.isPending || updateItemMutation.isPending}
          >
            {createItemMutation.isPending || updateItemMutation.isPending
              ? '저장 중...'
              : isEditing
              ? '수정'
              : '등록'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>품목 삭제</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            이 작업은 되돌릴 수 없습니다.
          </Alert>
          <Typography>
            <strong>{selectedItem?.name}</strong> 품목을 삭제하시겠습니까?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            취소
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteItemMutation.isPending}
          >
            {deleteItemMutation.isPending ? '삭제 중...' : '삭제'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ItemManagement;