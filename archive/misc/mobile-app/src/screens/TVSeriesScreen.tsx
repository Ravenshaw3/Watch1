import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  Alert,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { mediaApi } from '../services/api';
import { TVSeries } from '../types/media';

export default function TVSeriesScreen({ navigation }: any) {
  const [tvSeries, setTvSeries] = useState<TVSeries[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadTVSeries();
  }, []);

  const loadTVSeries = async () => {
    try {
      setLoading(true);
      const response = await mediaApi.getTVSeries();
      setTvSeries(response.series);
    } catch (error) {
      console.error('Failed to load TV series:', error);
      Alert.alert('Error', 'Failed to load TV series');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTVSeries();
    setRefreshing(false);
  };

  const selectSeries = (series: TVSeries) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    navigation.navigate('SeriesDetail', { series });
  };

  const getTotalEpisodes = (series: TVSeries): number => {
    return Object.values(series.seasons).reduce((total, episodes) => total + episodes.length, 0);
  };

  const renderSeriesCard = ({ item }: { item: TVSeries }) => (
    <TouchableOpacity
      style={styles.seriesCard}
      onPress={() => selectSeries(item)}
      activeOpacity={0.8}
    >
      <LinearGradient
        colors={['#3B82F6', '#1E40AF']}
        style={styles.seriesImage}
      >
        <Ionicons name="tv" size={40} color="white" />
      </LinearGradient>
      
      <View style={styles.seriesInfo}>
        <Text style={styles.seriesName} numberOfLines={2}>
          {item.series_name}
        </Text>
        <Text style={styles.seriesMeta}>
          {Object.keys(item.seasons).length} Season{Object.keys(item.seasons).length !== 1 ? 's' : ''} • {getTotalEpisodes(item)} Episodes
        </Text>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="tv-outline" size={80} color="#9CA3AF" />
      <Text style={styles.emptyTitle}>No TV Series Found</Text>
      <Text style={styles.emptySubtitle}>
        Scan your media directory to discover TV shows
      </Text>
      <TouchableOpacity style={styles.scanButton} onPress={loadTVSeries}>
        <Text style={styles.scanButtonText}>Scan Media</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading TV Series...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={tvSeries}
        renderItem={renderSeriesCard}
        keyExtractor={(item) => item.series_name}
        numColumns={2}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={renderEmptyState}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
  },
  listContainer: {
    padding: 16,
  },
  seriesCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    margin: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  seriesImage: {
    height: 120,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  seriesInfo: {
    padding: 12,
  },
  seriesName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  seriesMeta: {
    fontSize: 12,
    color: '#6B7280',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
  },
  scanButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  scanButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

