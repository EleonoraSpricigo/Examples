from mpi4py import MPI
import numpy as np
import KratosMultiphysics.RomApplication.tsqr
from KratosMultiphysics.RomApplication.randomized_singular_value_decomposition import RandomizedSingularValueDecomposition

if __name__ == "__main__":
    comm = MPI.COMM_WORLD      # Communications macro
    svd_truncation_tolerance = 1e-6
    rank = comm.Get_rank()
    size = comm.Get_size()
    send_data=None
    rows = None
    if rank==0:
        TestMatrix = np.load("SnapshotsMatrix.npy")
        rows = TestMatrix.shape[0]
        cols = TestMatrix.shape[1]
        # Split into sub-arrays along required axis
        arrs = np.array_split(TestMatrix, size, axis=0)
        # Flatten the sub-arrays
        raveled = [np.ravel(arr) for arr in arrs]
        rank_rows_list = [arr.shape[0] for arr in arrs]
        # Join them back up into a 1D array
        send_data = np.concatenate(raveled)
    else:
        cols = None
        rank_rows_list = None
    cols = comm.bcast(cols, root=0)
    rank_rows_list = comm.bcast(rank_rows_list, root=0)

    recvbuf = np.empty((rank_rows_list[rank], int(cols)))
    comm.Scatterv(send_data, recvbuf, root=0)

    Qi,Bi = KratosMultiphysics.RomApplication.tsqr.randomized_orthogonalization(
        recvbuf,comm,svd_truncation_tolerance,1)
    U_final,s,v = KratosMultiphysics.RomApplication.tsqr.svd_parallel(Qi, Bi, comm,
        epsilon=svd_truncation_tolerance)

    U_global = None
    U_global = np.array(comm.gather(U_final, root=0))

    U_local = None
    if rank==0:
        rank_rows_list = np.cumsum(rank_rows_list)
        rank_rows_list = np.insert(rank_rows_list, 0, 0)
        U_local = np.zeros((rows,U_global.shape[2]))
        for i in range(0,size):
            idxg, idyg = rank_rows_list[i], rank_rows_list[i+1]
            U_local[idxg:idyg,:] = U_global[i,:,:]

        Randomized_Reconstruction = U_local@np.diag(s)@v.T #reconstruct matrix

        #Check that the difference of the reconstruction is below a tolerance
        print( "The error or reconstruction is: ", np.linalg.norm(Randomized_Reconstruction - TestMatrix)/np.linalg.norm(TestMatrix))

        # Wirte the left singular values
        np.save("LeftSingularVectors.npy", U_local)